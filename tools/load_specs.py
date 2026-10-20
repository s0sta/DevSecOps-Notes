"""Read the POSTS[...] = dict(...) specs from the GIF builder files WITHOUT running them (ast + literal_eval)."""
import ast, pathlib, sys, json

def load(root):
    out = {}
    for f in sorted(pathlib.Path(root).glob("*/*/Code/posts_*.py")):
        tree = ast.parse(f.read_text(encoding="utf-8"))
        for node in tree.body:
            if not isinstance(node, ast.Assign) or len(node.targets) != 1:
                continue
            t = node.targets[0]
            if not (isinstance(t, ast.Subscript) and isinstance(t.value, ast.Name) and t.value.id == "POSTS"):
                continue
            try:
                key = ast.literal_eval(t.slice)
            except Exception:
                continue
            v = node.value
            spec = {}
            if isinstance(v, ast.Call) and getattr(v.func, "id", "") == "dict":
                for kw in v.keywords:
                    try:
                        spec[kw.arg] = ast.literal_eval(kw.value)
                    except Exception:
                        spec[kw.arg] = "<<non-literal>>"
            elif isinstance(v, ast.Dict):
                try:
                    spec = ast.literal_eval(v)
                except Exception:
                    spec = {"_err": "dict not literal"}
            spec["_file"] = f.name
            out[int(key)] = spec
    return out

if __name__ == "__main__":
    specs = load(sys.argv[1])
    print(len(specs), "specs", min(specs), max(specs))
    import collections
    lay = collections.defaultdict(set)
    for n, s in specs.items():
        lay[s.get("layout", "?")].update(k for k in s if not k.startswith("_"))
    for k, v in sorted(lay.items()):
        print(f"{k:14s} {sorted(v)}")
    nonlit = [(n, k) for n, s in specs.items() for k, v in s.items() if v == "<<non-literal>>"]
    print("non-literal fields:", nonlit[:20], len(nonlit))
    json.dump(specs, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
