#!/usr/bin/env python3
"""
parse-transcript.py
将上传的面试文字记录（.txt / .md）解析为结构化的问答列表，
方便 Claude 逐题进行复盘分析。

用法：
    python scripts/parse-transcript.py <input_file>

输出：
    打印结构化的 JSON，包含每道题的题目和用户回答
"""

import sys
import json
import re

def parse_transcript(filepath: str) -> list[dict]:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    qa_pairs = []

    # 尝试匹配常见格式：Q: ... A: ... 或 问：... 答：...
    patterns = [
        r"[Qq][：:]\s*(.+?)\s*[Aa][：:]\s*(.+?)(?=\n[Qq][：:]|\Z)",
        r"问[：:]\s*(.+?)\s*答[：:]\s*(.+?)(?=\n问[：:]|\Z)",
        r"面试官[：:]\s*(.+?)\s*我[：:]\s*(.+?)(?=\n面试官[：:]|\Z)",
    ]

    for pattern in patterns:
        matches = re.findall(pattern, content, re.DOTALL)
        if matches:
            for i, (q, a) in enumerate(matches, 1):
                qa_pairs.append({
                    "index": i,
                    "question": q.strip(),
                    "answer": a.strip()
                })
            return qa_pairs

    # 如果没有匹配到结构化格式，尝试按编号列表解析
    # 格式：1. 问题\n回答内容
    numbered = re.findall(r"\d+[\.、]\s*(.+?)(?=\n\d+[\.、]|\Z)", content, re.DOTALL)
    if numbered:
        for i, block in enumerate(numbered, 1):
            lines = block.strip().split("\n", 1)
            qa_pairs.append({
                "index": i,
                "question": lines[0].strip(),
                "answer": lines[1].strip() if len(lines) > 1 else "（未记录回答）"
            })
        return qa_pairs

    # 兜底：整体返回原文，提示 Claude 自行解析
    return [{
        "index": 1,
        "question": "（无法自动解析，原文如下）",
        "answer": content.strip()
    }]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python parse-transcript.py <input_file>")
        sys.exit(1)

    filepath = sys.argv[1]
    result = parse_transcript(filepath)
    print(json.dumps(result, ensure_ascii=False, indent=2))
