"""Topic and section of every post (checked by hand). i = IT notes, d = DevSecOps notes, b = both."""
TOPICS = {
    "L": "Linux", "ST": "Storage & infrastructure", "NE": "Networking & DNS", "WE": "Web servers, TLS & HTTP",
    "WI": "Windows & Active Directory", "SE": "Security & hardening", "BK": "Backup & recovery", "OP": "IT operations & incidents",
    "DB": "Databases & SQL", "DO": "DevOps basics", "CI": "Git & CI/CD", "DK": "Docker & containers", "K8": "Kubernetes",
    "IA": "Terraform, Ansible & IaC", "CL": "Cloud: AWS & Azure", "GO": "GitOps & Helm", "OB": "Observability & SRE",
    "PL": "Platform engineering", "CS": "DevSecOps & cloud security", "AI": "AI infrastructure & LLM security",
    "DA": "Data engineering", "PY": "Python scripts", "SH": "Shell scripts",
    "AP": "Application & API security", "SC": "Supply chain & SBOM", "VM": "Vulnerability management & attack surface",
    "IR": "Incident response & detection", "RE": "Release & build engineering",
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
372 CS d|373 AP d|374 AP d|375 AP d|376 AP d|377 PY d|378 VM d|379 CS d|380 VM d|381 CS d|382 SC d|383 CS d|384 AP d|385 AP d|386 SC d
387 PY d|388 SC d|389 SC d|390 VM d|391 SC d|392 CI d|393 CI d|394 IA d|395 CI d|396 PY d|397 PY d|398 SC d|399 CI d|400 CI d|401 CI d
402 AP d|403 AP d|404 AP d|405 AP d|406 PY d|407 AP d|408 AP d|409 AP d|410 AP d|411 AP d|412 IR d|413 IR d|414 IR d|415 PY d|416 PY d
417 IR d|418 IR d|419 CS d|420 IR d|421 IR d
422 RE d|423 RE d|424 RE d|425 PY d|426 PY d|427 RE d|428 RE d|429 RE d|430 RE d|431 RE d|432 RE d|433 RE d|434 RE d|435 PY d|436 PY d
437 RE d|438 RE d|439 RE d|440 RE d|441 RE d|442 DO d|443 DO d|444 DO d|445 PY d|446 PY d|447 DO d|448 DO d|449 DO d|450 DO d|451 DO d
452 OB d|453 OB d|454 OB d|455 PY d|456 PY d|457 OB d|458 OB d|459 OB d|460 OB d|461 OB d|462 PL d|463 CI d|464 PL d|465 PY d|466 PY d
467 CI d|468 PL d|469 CI d|470 PL d|471 PL d
472 NE b|473 NE b|474 PY b|475 PY b|476 WE b|477 NE b|478 NE b|479 NE b|480 NE b|481 NE b|482 NE b|483 NE b|484 NE b|485 PY b|486 PY b
487 NE b|488 NE b|489 NE b|490 NE b|491 NE b|492 CL d|493 CL d|494 CL d|495 PY d|496 PY d|497 CL d|498 CL d|499 CL d|500 CL d|501 CL d
502 K8 d|503 K8 d|504 K8 d|505 PY d|506 PY b|507 K8 d|508 K8 d|509 K8 d|510 K8 d|511 K8 d|512 NE b|513 NE b|514 NE b|515 PY b|516 PY b
517 NE b|518 NE b|519 NE b|520 NE b|521 NE b
522 CS d|523 PY d|524 CS d|525 PY b|526 PY b|527 CS d|528 PY d|529 PY b|530 PY b|531 CS d|532 SC d|533 SC d|534 SC d|535 PY d|536 PY d
537 SC d|538 SC d|539 PY d|540 PY d|541 SC d|542 CS d|543 CL d|544 CS d|545 PY d|546 PY d|547 CS d|548 K8 d|549 PY d|550 PY d|551 CS d
552 AP d|553 AP b|554 AP b|555 PY d|556 PY d|557 AP d|558 PY d|559 PY d|560 AP b|561 AP d|562 CS d|563 CS d|564 CS d|565 PY d|566 PY d
567 CS d|568 CS d|569 PY d|570 PY d|571 CS d
572 PY b|573 PY b|574 PY b|575 PY b|576 PY b|577 OP b|578 L b|579 L b|580 OP b|581 L b|582 PY b|583 PY d|584 PY b|585 PY b|586 PY b
587 SE b|588 SE b|589 SE b|590 SE b|591 SE b|592 PY d|593 PY d|594 PY d|595 PY d|596 PY d|597 K8 d|598 K8 d|599 K8 d|600 K8 d|601 K8 d
602 PY d|603 PY d|604 PY d|605 PY d|606 PY d|607 CI d|608 CI d|609 CI d|610 CI d|611 CI d|612 PY b|613 PY b|614 PY d|615 PY b|616 PY d
617 BK b|618 BK b|619 CL d|620 BK b|621 BK b
622 SH b|623 SH b|624 SH b|625 SH b|626 SH b|627 L b|628 L b|629 L b|630 L b|631 L b|632 SH b|633 SH b|634 SH b|635 SH b|636 SH b
637 SE b|638 SE b|639 SE b|640 SE b|641 SE b|642 SH d|643 SH d|644 SH d|645 SH d|646 SH d|647 CI d|648 CI d|649 CI d|650 CI d|651 CI d
652 SH b|653 SH b|654 SH b|655 SH b|656 SH b|657 SE b|658 SE b|659 SE b|660 SE b|661 SE b|662 SH b|663 SH b|664 SH b|665 SH b|666 SH b
667 OP b|668 L b|669 OP b|670 L b|671 L b
672 PY b|673 PY b|674 PY b|675 PY b|676 PY b|677 IR b|678 IR b|679 IR b|680 IR b|681 IR b|682 PY b|683 PY b|684 PY b|685 PY b|686 PY b
687 IR b|688 IR b|689 IR b|690 IR b|691 IR b|692 PY b|693 PY b|694 PY b|695 PY b|696 PY b|697 IR b|698 IR b|699 IR b|700 IR b|701 IR b
702 PY b|703 PY b|704 PY b|705 PY b|706 PY b|707 IR b|708 IR b|709 IR b|710 IR b|711 IR b|712 PY b|713 PY b|714 PY b|715 PY b|716 PY b
717 IR b|718 IR b|719 IR b|720 IR b|721 IR b
722 PY d|723 PY d|724 PY d|725 PY d|726 PY d|727 VM d|728 VM d|729 VM d|730 VM d|731 VM d|732 PY d|733 PY d|734 PY d|735 PY d|736 PY d
737 VM d|738 VM d|739 VM d|740 VM d|741 VM d|742 PY d|743 PY d|744 PY d|745 PY d|746 PY d|747 VM d|748 VM d|749 VM d|750 VM d|751 VM d
752 PY d|753 PY d|754 PY d|755 PY d|756 PY d|757 VM d|758 VM d|759 VM d|760 VM d|761 VM d|762 PY d|763 PY d|764 PY d|765 PY d|766 PY d
767 VM d|768 VM d|769 VM d|770 VM d|771 VM d
"""
SEC = {"i": ["it"], "d": ["devsecops"], "b": ["it", "devsecops"]}
ASSIGN = {}
for item in RAW.replace("\n", "|").split("|"):
    item = item.strip()
    if not item:
        continue
    n, t, s = item.split()
    ASSIGN[int(n)] = (TOPICS[t], SEC[s])
# Posts 72-771 are in RAW above. For new posts add "number topic section" items (section: i, d or b).
assert all(72 <= n for n in ASSIGN), "post numbers start at 72"
