"""Topic and section of every post (checked by hand). i = IT notes, d = DevSecOps notes, b = both."""
TOPICS = {
    "L": "Linux", "ST": "Storage & infrastructure", "NE": "Networking & DNS", "WE": "Web servers, TLS & HTTP",
    "WI": "Windows & Active Directory", "SE": "Security & hardening", "BK": "Backup & recovery", "OP": "IT operations & incidents",
    "DB": "Databases & SQL", "DO": "DevOps basics", "CI": "Git & CI/CD", "DK": "Docker & containers", "K8": "Kubernetes",
    "IA": "Terraform, Ansible & IaC", "CL": "Cloud: AWS & Azure", "GO": "GitOps & Helm", "OB": "Observability & SRE",
    "PL": "Platform engineering", "CS": "DevSecOps & cloud security", "AI": "AI infrastructure & LLM security",
    "DA": "Data engineering", "PY": "Python scripts",
}
RAW = """
72 WE i|73 L i|74 L i|75 L i|76 L i|77 L i|78 L i|79 L b|80 L i|81 SE b|82 WE i|83 ST i|84 WE b|85 BK i|86 ST i|87 NE i|88 L i|89 OP b|90 L b|91 OP i
92 L i|93 WI i|94 NE i|95 NE i|96 ST i|97 NE i|98 SE b|99 WE i|100 WI i|101 NE i|102 WI i|103 NE i|104 WE i|105 L i|106 NE i|107 L i|108 DK d|109 DK d
110 WI i|111 WE i|112 SE i|113 DK d|114 WI i|115 K8 d|116 OB b|117 SE b|118 ST i|119 SE b|120 WE i|121 DB i|122 OP i|123 WE b|124 SE b|125 SE i|126 CL d
127 NE b|128 WI b|129 ST b|130 WI i|131 NE i|132 CI d|133 DK d|134 CI d|135 L b|136 DO d|137 IA d|138 OP b|139 CL d|140 L b|141 DO d|142 K8 d|143 K8 d
144 DO d|145 CI d|146 IA d|147 DK d|148 WE i|149 IA d|150 OB d|151 NE i|152 DK d|153 CI d|154 CI d|155 CI d|156 K8 d|157 K8 d|158 IA d|159 CS d|160 K8 d
161 K8 d|162 K8 d|163 DK d|164 DK d|165 OB d|166 OB d|167 DO d|168 DB b|169 IA d|170 IA d|171 CL d|172 PY b|173 L b|174 ST b|175 ST b|176 L b|177 PY b
178 SE b|179 SE b|180 L b|181 L b|182 PY b|183 CL d|184 CL d|185 CL d|186 CL d|187 PY b|188 CS d|189 CL d|190 CS d|191 CL d|192 PY b|193 IA d|194 DK d
195 CI d|196 DK d|197 PY d|198 CI d|199 DK d|200 DO d|201 IA d|202 PY d|203 K8 d|204 K8 d|205 K8 d|206 K8 d|207 PY b|208 K8 d|209 K8 d|210 K8 d|211 K8 d
212 PY b|213 CS d|214 GO d|215 CS d|216 CS d|217 PY b|218 CS d|219 CS d|220 CS d|221 CS d|222 GO d|223 GO d|224 PY d|225 GO d|226 GO d|227 GO d|228 GO d
229 PY d|230 GO d|231 GO d|232 OB d|233 OB d|234 PY d|235 OB d|236 OB d|237 OB d|238 OB d|239 PY d|240 OB d|241 OB d|242 PL d|243 CI d|244 PY d|245 PL d
246 IA d|247 PL d|248 K8 d|249 PY d|250 PL d|251 PL d|252 CS d|253 CS d|254 PY d|255 CS d|256 CS d|257 CS d|258 CS d|259 PY d|260 CS d|261 CS d|262 AI d
263 AI d|264 PY d|265 AI d|266 AI d|267 AI d|268 AI d|269 PY d|270 AI d|271 AI d|272 CL d|273 ST i|274 L b|275 PY d|276 NE i|277 DK d|278 K8 d|279 NE i
280 PY b|281 NE i|282 CL d|283 CL d|284 CS d|285 PY d|286 CL d|287 CL d|288 CL d|289 CL d|290 PY d|291 CL d|292 K8 d|293 CI d|294 CI d|295 PY d|296 IA d
297 OB d|298 K8 d|299 CI d|300 PY d|301 DO d|302 SE b|303 WE b|304 SE b|305 PY b|306 CS d|307 CS d|308 CS d|309 CS d|310 PY d|311 CS d|312 AI d|313 AI d
314 AI d|315 PY d|316 AI d|317 AI d|318 AI d|319 AI d|320 PY d|321 AI d|322 DB i|323 DB i|324 DB i|325 PY i|326 DB i|327 DB i|328 DB i|329 DB i|330 PY i
331 DB i|332 DB i|333 DB i|334 DB i|335 PY i|336 DB i|337 DB i|338 DB i|339 DB i|340 PY i|341 DB i|342 DB i|343 DB i|344 DB i|345 PY i|346 DB i|347 DB i
348 DB i|349 DB i|350 PY i|351 DB i|352 DA d|353 DA d|354 DA d|355 PY d|356 DA d|357 DA d|358 DA d|359 DA d|360 PY d|361 DA d|362 DA d|363 DA d|364 DA d
365 PY d|366 DA d|367 DA d|368 DA d|369 DA d|370 PY d|371 DA d
"""
SEC = {"i": ["it"], "d": ["devsecops"], "b": ["it", "devsecops"]}
ASSIGN = {}
for item in RAW.replace("\n", "|").split("|"):
    item = item.strip()
    if not item:
        continue
    n, t, s = item.split()
    ASSIGN[int(n)] = (TOPICS[t], SEC[s])
# Posts 72-371 are in RAW above. For new posts add "number topic section" items (section: i, d or b).
assert all(72 <= n for n in ASSIGN), "post numbers start at 72"
