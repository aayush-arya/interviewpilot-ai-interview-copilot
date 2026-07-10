"""Seed demo users, badges and coding problems. Idempotent.

Run: python -m app.seed
"""
import json

from app.core.security import hash_password
from app.db.session import Base, SessionLocal, engine
from app.models import Badge, CodingProblem, User
from app.services.gamification_service import BADGE_DEFS

PROBLEMS = [
    {
        "title": "Two Sum",
        "slug": "two-sum",
        "difficulty": "easy",
        "topic": "arrays",
        "description": (
            "Given a list of integers and a target, print the **indices** (0-based, space-"
            "separated, ascending) of the two numbers that add up to the target.\n\n"
            "**Input format**: line 1 = space-separated integers, line 2 = target.\n"
            "**Output format**: `i j`\n\n**Example**\n```\ninput:  2 7 11 15\n        9\noutput: 0 1\n```"
        ),
        "starter": {
            "python": 'nums = list(map(int, input().split()))\ntarget = int(input())\n\n# print two indices, e.g. print(i, j)\n',
            "javascript": "const lines = require('fs').readFileSync(0, 'utf8').split('\\n');\nconst nums = lines[0].trim().split(/\\s+/).map(Number);\nconst target = Number(lines[1]);\n\n// console.log(i, j)\n",
            "java": "import java.util.*;\npublic class Main {\n  public static void main(String[] args) {\n    Scanner sc = new Scanner(System.in);\n    // read, solve, print \"i j\"\n  }\n}\n",
            "cpp": "#include <bits/stdc++.h>\nusing namespace std;\nint main() {\n  // read, solve, print \"i j\"\n  return 0;\n}\n",
        },
        "visible": [
            {"input": "2 7 11 15\n9", "expected": "0 1"},
            {"input": "3 2 4\n6", "expected": "1 2"},
        ],
        "hidden": [
            {"input": "3 3\n6", "expected": "0 1"},
            {"input": "1 5 9 13 20 7\n27", "expected": "4 5"},
        ],
    },
    {
        "title": "Valid Parentheses",
        "slug": "valid-parentheses",
        "difficulty": "easy",
        "topic": "stacks",
        "description": (
            "Given a string of brackets `()[]{}`, print `true` if it is valid (every bracket "
            "closed in the correct order), else `false`.\n\n**Input**: one line.\n"
            "**Output**: `true` or `false`.\n\n**Example**: `([]{})` → `true`"
        ),
        "starter": {
            "python": "s = input().strip()\n\n# print('true' or 'false')\n",
            "javascript": "const s = require('fs').readFileSync(0, 'utf8').trim();\n\n// console.log('true' or 'false')\n",
            "java": "import java.util.*;\npublic class Main {\n  public static void main(String[] args) {\n    String s = new Scanner(System.in).nextLine().trim();\n    // print true/false\n  }\n}\n",
            "cpp": "#include <bits/stdc++.h>\nusing namespace std;\nint main() {\n  string s; cin >> s;\n  // print true/false\n  return 0;\n}\n",
        },
        "visible": [
            {"input": "([]{})", "expected": "true"},
            {"input": "([)]", "expected": "false"},
        ],
        "hidden": [
            {"input": "(", "expected": "false"},
            {"input": "{[()()]}", "expected": "true"},
        ],
    },
    {
        "title": "Longest Substring Without Repeating Characters",
        "slug": "longest-substring-norepeat",
        "difficulty": "medium",
        "topic": "sliding window",
        "description": (
            "Given a string, print the **length** of the longest substring without repeating "
            "characters.\n\n**Example**: `abcabcbb` → `3` (\"abc\")"
        ),
        "starter": {
            "python": "s = input().strip()\n\n# print(length)\n",
            "javascript": "const s = require('fs').readFileSync(0, 'utf8').trim();\n\n// console.log(length)\n",
            "java": "import java.util.*;\npublic class Main {\n  public static void main(String[] args) {\n    String s = new Scanner(System.in).nextLine().trim();\n    // print length\n  }\n}\n",
            "cpp": "#include <bits/stdc++.h>\nusing namespace std;\nint main() {\n  string s; cin >> s;\n  // print length\n  return 0;\n}\n",
        },
        "visible": [
            {"input": "abcabcbb", "expected": "3"},
            {"input": "bbbbb", "expected": "1"},
        ],
        "hidden": [
            {"input": "pwwkew", "expected": "3"},
            {"input": "abcdefghija", "expected": "10"},
        ],
    },
    {
        "title": "Merge Intervals",
        "slug": "merge-intervals",
        "difficulty": "medium",
        "topic": "sorting",
        "description": (
            "Line 1: n (number of intervals). Next n lines: `start end`. Merge overlapping "
            "intervals and print each merged interval on its own line, sorted by start.\n\n"
            "**Example**\n```\ninput:  4\n        1 3\n        2 6\n        8 10\n        15 18\noutput: 1 6\n        8 10\n        15 18\n```"
        ),
        "starter": {
            "python": "n = int(input())\nintervals = [tuple(map(int, input().split())) for _ in range(n)]\n\n# print merged intervals\n",
            "javascript": "const lines = require('fs').readFileSync(0, 'utf8').trim().split('\\n');\nconst n = Number(lines[0]);\nconst intervals = lines.slice(1, 1 + n).map(l => l.trim().split(/\\s+/).map(Number));\n\n// print merged intervals\n",
            "java": "import java.util.*;\npublic class Main {\n  public static void main(String[] args) {\n    // read, merge, print\n  }\n}\n",
            "cpp": "#include <bits/stdc++.h>\nusing namespace std;\nint main() {\n  // read, merge, print\n  return 0;\n}\n",
        },
        "visible": [
            {"input": "4\n1 3\n2 6\n8 10\n15 18", "expected": "1 6\n8 10\n15 18"},
        ],
        "hidden": [
            {"input": "2\n1 4\n4 5", "expected": "1 5"},
            {"input": "1\n5 7", "expected": "5 7"},
        ],
    },
    {
        "title": "Course Schedule (Cycle Detection)",
        "slug": "course-schedule",
        "difficulty": "hard",
        "topic": "graphs",
        "description": (
            "Line 1: `n m` (courses, prerequisite pairs). Next m lines: `a b` meaning course a "
            "requires course b first. Print `true` if all courses can be finished (no cycle), "
            "else `false`."
        ),
        "starter": {
            "python": "n, m = map(int, input().split())\nedges = [tuple(map(int, input().split())) for _ in range(m)]\n\n# print('true' or 'false')\n",
            "javascript": "const lines = require('fs').readFileSync(0, 'utf8').trim().split('\\n');\nconst [n, m] = lines[0].trim().split(/\\s+/).map(Number);\nconst edges = lines.slice(1, 1 + m).map(l => l.trim().split(/\\s+/).map(Number));\n\n// console.log('true' or 'false')\n",
            "java": "import java.util.*;\npublic class Main {\n  public static void main(String[] args) {\n    // read, detect cycle, print true/false\n  }\n}\n",
            "cpp": "#include <bits/stdc++.h>\nusing namespace std;\nint main() {\n  // read, detect cycle, print true/false\n  return 0;\n}\n",
        },
        "visible": [
            {"input": "2 1\n1 0", "expected": "true"},
            {"input": "2 2\n1 0\n0 1", "expected": "false"},
        ],
        "hidden": [
            {"input": "4 3\n1 0\n2 1\n3 2", "expected": "true"},
            {"input": "3 3\n0 1\n1 2\n2 0", "expected": "false"},
        ],
    },
    {
        "title": "Maximum Subarray",
        "slug": "maximum-subarray",
        "difficulty": "medium",
        "topic": "dynamic programming",
        "description": (
            "Given a list of integers (one line, space-separated), print the **sum** of the "
            "contiguous subarray with the largest sum (Kadane's algorithm).\n\n"
            "**Example**: `-2 1 -3 4 -1 2 1 -5 4` → `6` (subarray `4 -1 2 1`)"
        ),
        "starter": {
            "python": "nums = list(map(int, input().split()))\n\n# print(max_sum)\n",
            "javascript": "const nums = require('fs').readFileSync(0, 'utf8').trim().split(/\\s+/).map(Number);\n\n// console.log(maxSum)\n",
            "java": "import java.util.*;\npublic class Main {\n  public static void main(String[] args) {\n    // read ints from one line, print max subarray sum\n  }\n}\n",
            "cpp": "#include <bits/stdc++.h>\nusing namespace std;\nint main() {\n  // read ints, print max subarray sum\n  return 0;\n}\n",
        },
        "visible": [
            {"input": "-2 1 -3 4 -1 2 1 -5 4", "expected": "6"},
            {"input": "1", "expected": "1"},
        ],
        "hidden": [
            {"input": "5 4 -1 7 8", "expected": "23"},
            {"input": "-1 -2 -3", "expected": "-1"},
        ],
    },
    {
        "title": "Binary Search",
        "slug": "binary-search",
        "difficulty": "easy",
        "topic": "binary search",
        "description": (
            "Line 1: a **sorted** list of distinct integers. Line 2: a target. "
            "Print the target's index (0-based), or `-1` if absent. Must run in O(log n).\n\n"
            "**Example**: `-1 0 3 5 9 12` + target `9` → `4`"
        ),
        "starter": {
            "python": "nums = list(map(int, input().split()))\ntarget = int(input())\n\n# print(index or -1)\n",
            "javascript": "const lines = require('fs').readFileSync(0, 'utf8').trim().split('\\n');\nconst nums = lines[0].trim().split(/\\s+/).map(Number);\nconst target = Number(lines[1]);\n\n// console.log(index or -1)\n",
            "java": "import java.util.*;\npublic class Main {\n  public static void main(String[] args) {\n    // read sorted ints + target, print index or -1\n  }\n}\n",
            "cpp": "#include <bits/stdc++.h>\nusing namespace std;\nint main() {\n  // read sorted ints + target, print index or -1\n  return 0;\n}\n",
        },
        "visible": [
            {"input": "-1 0 3 5 9 12\n9", "expected": "4"},
            {"input": "-1 0 3 5 9 12\n2", "expected": "-1"},
        ],
        "hidden": [
            {"input": "1\n1", "expected": "0"},
            {"input": "1 3\n3", "expected": "1"},
        ],
    },
    {
        "title": "Valid Anagram",
        "slug": "valid-anagram",
        "difficulty": "easy",
        "topic": "hashing",
        "description": (
            "Two lines: strings `s` and `t`. Print `true` if `t` is an anagram of `s`, else `false`.\n\n"
            "**Example**: `anagram` / `nagaram` → `true`"
        ),
        "starter": {
            "python": "s = input().strip()\nt = input().strip()\n\n# print('true' or 'false')\n",
            "javascript": "const lines = require('fs').readFileSync(0, 'utf8').split('\\n');\nconst s = lines[0].trim(), t = (lines[1] || '').trim();\n\n// console.log('true' or 'false')\n",
            "java": "import java.util.*;\npublic class Main {\n  public static void main(String[] args) {\n    Scanner sc = new Scanner(System.in);\n    String s = sc.nextLine().trim(), t = sc.nextLine().trim();\n    // print true/false\n  }\n}\n",
            "cpp": "#include <bits/stdc++.h>\nusing namespace std;\nint main() {\n  string s, t; cin >> s >> t;\n  // print true/false\n  return 0;\n}\n",
        },
        "visible": [
            {"input": "anagram\nnagaram", "expected": "true"},
            {"input": "rat\ncar", "expected": "false"},
        ],
        "hidden": [
            {"input": "a\nab", "expected": "false"},
            {"input": "listen\nsilent", "expected": "true"},
        ],
    },
    {
        "title": "Product of Array Except Self",
        "slug": "product-except-self",
        "difficulty": "medium",
        "topic": "arrays",
        "description": (
            "Given a list of integers, print a list where each position holds the product of "
            "**all other** elements (space-separated). No division; O(n).\n\n"
            "**Example**: `1 2 3 4` → `24 12 8 6`"
        ),
        "starter": {
            "python": "nums = list(map(int, input().split()))\n\n# print(' '.join(map(str, result)))\n",
            "javascript": "const nums = require('fs').readFileSync(0, 'utf8').trim().split(/\\s+/).map(Number);\n\n// console.log(result.join(' '))\n",
            "java": "import java.util.*;\npublic class Main {\n  public static void main(String[] args) {\n    // read ints, print products space-separated\n  }\n}\n",
            "cpp": "#include <bits/stdc++.h>\nusing namespace std;\nint main() {\n  // read ints, print products space-separated\n  return 0;\n}\n",
        },
        "visible": [
            {"input": "1 2 3 4", "expected": "24 12 8 6"},
        ],
        "hidden": [
            {"input": "2 3", "expected": "3 2"},
            {"input": "-1 1 0 -3 3", "expected": "0 0 9 0 0"},
        ],
    },
    {
        "title": "Coin Change",
        "slug": "coin-change",
        "difficulty": "hard",
        "topic": "dynamic programming",
        "description": (
            "Line 1: coin denominations. Line 2: amount. Print the **fewest** coins needed to "
            "make the amount, or `-1` if impossible.\n\n"
            "**Example**: coins `1 2 5`, amount `11` → `3` (5+5+1)"
        ),
        "starter": {
            "python": "coins = list(map(int, input().split()))\namount = int(input())\n\n# print(min_coins or -1)\n",
            "javascript": "const lines = require('fs').readFileSync(0, 'utf8').trim().split('\\n');\nconst coins = lines[0].trim().split(/\\s+/).map(Number);\nconst amount = Number(lines[1]);\n\n// console.log(minCoins or -1)\n",
            "java": "import java.util.*;\npublic class Main {\n  public static void main(String[] args) {\n    // read coins + amount, print fewest coins or -1\n  }\n}\n",
            "cpp": "#include <bits/stdc++.h>\nusing namespace std;\nint main() {\n  // read coins + amount, print fewest coins or -1\n  return 0;\n}\n",
        },
        "visible": [
            {"input": "1 2 5\n11", "expected": "3"},
            {"input": "2\n3", "expected": "-1"},
        ],
        "hidden": [
            {"input": "1\n0", "expected": "0"},
            {"input": "186 419 83 408\n6249", "expected": "20"},
        ],
    },
]


def seed() -> None:
    import app.models  # noqa: F401
    from app.problem_bank import bank_problems

    all_problems = PROBLEMS + bank_problems()
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if not db.query(User).filter(User.email == "demo@user.com").first():
            db.add(User(email="demo@user.com", hashed_password=hash_password("Demo@1234"),
                        full_name="Demo User", target_role="Backend Engineer"))
        if not db.query(User).filter(User.email == "admin@user.com").first():
            db.add(User(email="admin@user.com", hashed_password=hash_password("Admin@1234"),
                        full_name="Admin", role="admin"))
        for code, name, description, icon in BADGE_DEFS:
            if not db.query(Badge).filter(Badge.code == code).first():
                db.add(Badge(code=code, name=name, description=description, icon=icon))
        for p in all_problems:
            if not db.query(CodingProblem).filter(CodingProblem.slug == p["slug"]).first():
                db.add(CodingProblem(
                    title=p["title"], slug=p["slug"], description=p["description"],
                    difficulty=p["difficulty"], topic=p["topic"],
                    starter_code_json=json.dumps(p["starter"]),
                    visible_tests_json=json.dumps(p["visible"]),
                    hidden_tests_json=json.dumps(p["hidden"]),
                ))
        db.commit()
    print("Seed complete: demo@user.com / Demo@1234, admin@user.com / Admin@1234, "
          f"{len(all_problems)} coding problems, {len(BADGE_DEFS)} badges.")


if __name__ == "__main__":
    seed()
