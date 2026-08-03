import urllib.request
import json

url = "https://credit-rating-simulator.web.app/api/projects/SolairePower"
opener = urllib.request.build_opener(urllib.request.ProxyHandler())
req = urllib.request.Request(url)
resp = opener.open(req)
data = json.loads(resp.read().decode('utf-8'))

score = data.get("score", {})
null_reg = score.get("null_register", [])

print("================================================================================")
print("RENDERED HTML TABLE ROWS FOR /results/SolairePower MISSING CRITICAL FIELDS")
print("================================================================================")

table_rows_html = []
for f in null_reg:
    field_name = f.get("field")
    sub_factor = f.get("sub_factor")
    severity = f.get("points_forgone")
    row = f"""<tr>
    <td><code>{field_name}</code></td>
    <td>{sub_factor}</td>
    <td><span style="color: var(--accent-red); font-weight: 700;">{severity}</span></td>
</tr>"""
    table_rows_html.append(row)

rendered_table_html = f"""<table class="data-table">
    <thead>
        <tr>
            <th>Missing Field Name</th>
            <th>CORE Sub-Factor Impact</th>
            <th>Severity</th>
        </tr>
    </thead>
    <tbody>
{chr(10).join(table_rows_html)}
    </tbody>
</table>"""

print(rendered_table_html)
print("================================================================================")
