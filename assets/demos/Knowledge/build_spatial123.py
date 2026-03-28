import json
import pathlib
import re

base = pathlib.Path(__file__).resolve().parent
sources = ["knowledge1.html", "knowledge2.html", "knowledge3.html"]
items = []

for i, name in enumerate(sources, start=1):
    text = (base / name).read_text(encoding="utf-8")

    q = re.search(r'<p class="user-question">([\s\S]*?)</p>', text)
    img = re.search(r'<img class="problem-image" src="([^"]+)"', text)
    a = re.search(r'<(?:pre|div) class="assistant-scroll"[^>]*>([\s\S]*?)</(?:pre|div)>', text)

    question = re.sub(r"\s+", " ", q.group(1)).strip() if q else f"Demo {i} question"
    image = img.group(1).strip() if img else ""
    assistant = a.group(1).strip() if a else "&lt;answer&gt;No content&lt;/answer&gt;"

    items.append({
        "demo": f"Demo{i}",
        "question": question,
        "image": image,
        "assistant": assistant,
    })

payload = json.dumps(items, ensure_ascii=False)

html = f'''<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Knowledge & Recognition Demos</title>
    <style>
        :root {{
            --bg: #f5f6fa;
            --card: #ffffff;
            --line: #d6e1ee;
            --text: #0D2137;
            --muted: #697084;
            --brand: #1976D2;
            --prompt-bg: #ffffff;
            --prompt-border: #1976D2;
            --prompt-text: #0D2137;
        }}

        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            padding: 36px 20px;
            background: var(--bg);
            color: var(--text);
            font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }}

        .wrap {{
            max-width: 880px;
            margin: 0 auto;
        }}

        .chat-card {{
            background: var(--card);
            border: 1px solid var(--line);
            border-radius: 12px;
            overflow: hidden;
        }}

        .chat-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
            padding: 14px 16px;
            border-bottom: 1px solid var(--line);
            font-size: 16px;
            font-weight: 600;
        }}

        .header-left {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .demo {{
            color: var(--brand);
        }}

        .pager {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .step {{
            color: var(--muted);
            font-weight: 600;
            min-width: 36px;
            text-align: center;
        }}

        .nav-btn {{
            border: 1px solid var(--line);
            background: #fff;
            color: var(--text);
            border-radius: 8px;
            padding: 4px 10px;
            font-size: 13px;
            cursor: pointer;
        }}

        .nav-btn:disabled {{
            opacity: 0.4;
            cursor: not-allowed;
        }}

        .chat-body {{
            padding: 18px 16px 22px;
            background: #fbfcff;
        }}

        .user-turn {{
            margin: 0;
            width: 100%;
            background: var(--prompt-bg);
            border: 0.9px solid var(--prompt-border);
            border-radius: 3px;
            padding: 10px;
        }}

        .user-question {{
            margin: 0 0 10px;
            font-size: 17px;
            line-height: 1.5;
            color: var(--prompt-text);
        }}

        .problem-image {{
            width: 100%;
            border: 1px solid #dde1ec;
            border-radius: 8px;
            display: block;
            object-fit: cover;
            background: #fff;
        }}

        .assistant-turn {{
            margin-top: 16px;
            padding-right: 0;
            max-width: 100%;
        }}

        .assistant-head {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 8px;
            font-weight: 700;
            color: var(--text);
        }}

        .assistant-icon {{
            width: 20px;
            height: 20px;
            border-radius: 5px;
            background: #1976D2;
            color: white;
            display: grid;
            place-items: center;
            font-size: 12px;
            font-weight: 700;
        }}

        .assistant-content {{
            border: 0.9px solid var(--prompt-border);
            border-radius: 3px;
            background: #ffffff;
            padding: 10px;
            color: var(--prompt-text);
        }}

        .assistant-scroll {{
            margin: 0;
            white-space: pre-wrap;
            word-break: break-word;
            max-height: 560px;
            overflow: auto;
            font-size: 15px;
            line-height: 1.55;
            color: var(--prompt-text);
            font-family: inherit;
        }}
    </style>
</head>

<body>
    <main class="wrap">
        <section class="chat-card" aria-label="Example conversation">
            <header class="chat-header">
                <div class="header-left">
                    <span class="demo" id="demoLabel">Demo1</span>
                </div>
                <div class="pager">
                    <button class="nav-btn" id="prevBtn">Prev</button>
                    <span class="step" id="stepLabel">1/3</span>
                    <button class="nav-btn" id="nextBtn">Next</button>
                </div>
            </header>

            <div class="chat-body">
                <article class="user-turn" aria-label="User message with image and question">
                    <p class="user-question" id="questionText"></p>
                    <img class="problem-image" id="problemImage" src="" alt="Knowledge problem screenshot" />
                </article>

                <article class="assistant-turn" aria-label="Model response">
                    <div class="assistant-head">
                        <span class="assistant-icon">✦</span>
                        <span>Vero</span>
                    </div>
                    <div class="assistant-content">
                        <div class="assistant-scroll" id="assistantText"></div>
                    </div>
                </article>
            </div>
        </section>
    </main>

    <script>
        const DEMOS = {payload};
        let index = 0;

        const demoLabel = document.getElementById('demoLabel');
        const stepLabel = document.getElementById('stepLabel');
        const questionText = document.getElementById('questionText');
        const problemImage = document.getElementById('problemImage');
        const assistantText = document.getElementById('assistantText');
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');

        function normalizeAssistant(raw) {{
            const lines = String(raw).replace(/\\r\\n/g, '\\n').split('\\n');

            while (lines.length && lines[0].trim() === '') lines.shift();
            while (lines.length && lines[lines.length - 1].trim() === '') lines.pop();

            const isTagLine = (line) => /^\s*&lt;\/?(think|answer)&gt;\s*$/i.test(line);

            let minIndent = Infinity;
            for (const line of lines) {{
                if (!line.trim()) continue;
                if (isTagLine(line)) continue;
                const match = line.match(/^[ \t]*/);
                const indent = match ? match[0].length : 0;
                if (indent < minIndent) minIndent = indent;
            }}

            if (!Number.isFinite(minIndent)) minIndent = 0;

            return lines
                .map((line) => {{
                    if (isTagLine(line)) return line.trim();
                    if (!line.trim()) return '';
                    return line.slice(Math.min(minIndent, line.match(/^[ \t]*/)?.[0].length ?? 0)).trimEnd();
                }})
                .join('\\n');
        }}

        function render() {{
            const item = DEMOS[index];
            demoLabel.textContent = item.demo;
            stepLabel.textContent = `${{index + 1}}/${{DEMOS.length}}`;
            questionText.textContent = item.question;
            problemImage.src = item.image;
            problemImage.style.display = item.image ? 'block' : 'none';
            assistantText.innerHTML = normalizeAssistant(item.assistant);

            prevBtn.disabled = index === 0;
            nextBtn.disabled = index === DEMOS.length - 1;
        }}

        prevBtn.addEventListener('click', () => {{ if (index > 0) {{ index--; render(); }} }});
        nextBtn.addEventListener('click', () => {{ if (index < DEMOS.length - 1) {{ index++; render(); }} }});

        render();
    </script>
</body>

</html>
'''

(base / "knowledge123.html").write_text(html, encoding="utf-8")
print("Wrote static knowledge123.html with inline DEMOS from knowledge1/2/3")
