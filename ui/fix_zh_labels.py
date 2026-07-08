from pathlib import Path

p = Path(r'c:\Users\yujiashi\Desktop\SmartSuite_Phase1\ui\gen_wiki.py')
content = p.read_text(encoding='utf-8')

# Add zh_impact dict after zh_caps dict
old = "for t in tools:\n    tid = t['id']"
new = """zh_impact = {
    'zhiku': [('7','AI \u5e73\u53f0'),('Real-time','\u77ed\u8bed\u65f6\u6548'),('3-5x','\u6bcf\u4e3b\u9898\u53d8\u4f53'),('35','\u8bdd\u9898\u7c7b\u522b')],
    'zhizao': [('3hrs\u219210min','\u5355\u7bc7\u751f\u6210'),('800-3000','\u6bcf\u7bc7\u5b57\u6570'),('100%','GEO \u5408\u89c4'),('100+/\u6708','\u6708\u4ea7\u6587\u7ae0')],
    'zhiyou': [('+25%','\u8bc4\u5206\u63d0\u5347'),('5 \u7ef4','\u8bc4\u5206\u7ef4\u5ea6'),('100%','\u5408\u89c4\u901a\u8fc7'),('\u81ea\u52a8','\u8bc4\u5206\u2192\u91cd\u5199\u2192\u9a8c\u8bc1')],
    'zhibu': [('30\u21922min','\u5355\u7bc7\u53d1\u5e03'),('0 \u9519\u8bef','\u683c\u5f0f\u51c6\u786e'),('\u6279\u91cf','\u591a\u6587\u7ae0\u5904\u7406'),('JSON','CMS \u5c31\u7eea')],
    'zhichuan': [('\u5f85\u5b9a','\u6e20\u9053\u6570'),('\u81ea\u52a8','\u5b9a\u65f6\u53d1\u5e03'),('A/B','\u53d8\u4f53\u6d4b\u8bd5'),('\u591a\u5e73\u53f0','\u96c6\u6210')],
    'zhixi': [('\u5b9e\u65f6','E2E \u6570\u636e'),('Input+Output','\u5168\u6f0f\u6597'),('\u53ef\u6267\u884c','\u6d1e\u5bdf\u53d1\u73b0'),('\u5df2\u9a8c\u8bc1','Input \u6709\u6548\u6027')],
    'zhishu': [('E2E','\u5168\u6d41\u7a0b\u81ea\u52a8'),('7 \u6761','\u51b3\u7b56\u5f15\u64ce'),('8h/\u5468','\u8282\u7701\u4eba\u5de5'),('\u81ea\u52a8','\u884c\u52a8\u8ba1\u5212')],
    's3': [('\u221e','\u5f39\u6027\u6269\u5c55'),('99.99%','\u6301\u4e45\u6027'),('8\u6a21\u5757','\u6570\u636e\u4e92\u901a'),('\u7248\u672c\u5316','\u5b8c\u6574\u5ba1\u8ba1')],
}

for t in tools:
    tid = t['id']"""

content = content.replace(old, new, 1)

# Now use zh_impact in the ZH sections loop
# Replace the impact_html line in ZH section to use zh_impact
old_impact = """    impact_html = ''.join(
        f'<div style="background:#1a1d2e;border:1px solid #2a2f4a;border-radius:10px;padding:16px;"><div style="font-size:18px;font-weight:700;color:{t["color"]};">{v}</div><div style="font-size:10px;color:#7a82a0;text-transform:uppercase;">{l}</div></div>'
        for v, l in t['impact']
    )"""

new_impact = """    impact_data = zh_impact.get(tid, t['impact'])
    impact_html = ''.join(
        f'<div style="background:#1a1d2e;border:1px solid #2a2f4a;border-radius:10px;padding:16px;"><div style="font-size:18px;font-weight:700;color:{t["color"]};">{v}</div><div style="font-size:10px;color:#7a82a0;text-transform:uppercase;">{l}</div></div>'
        for v, l in impact_data
    )"""

# Only replace the second occurrence (ZH section)
first_pos = content.find(old_impact)
if first_pos >= 0:
    second_pos = content.find(old_impact, first_pos + len(old_impact))
    if second_pos >= 0:
        content = content[:second_pos] + new_impact + content[second_pos + len(old_impact):]
        print("Replaced ZH impact to use zh_impact dict")
    else:
        print("Second occurrence not found")
else:
    print("Pattern not found at all")

p.write_text(content, encoding='utf-8')
print("Done")
