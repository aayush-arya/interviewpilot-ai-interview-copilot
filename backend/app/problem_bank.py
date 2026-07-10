"""Extended coding-problem bank (51 problems).

Every problem carries a REFERENCE SOLUTION. Expected outputs are computed by
running that solution against the test inputs at seed time, so hidden/visible
test cases can never be wrong. Starter code is generated per language from the
problem's declared input pattern.
"""
import math
from collections import Counter, defaultdict, deque
from functools import lru_cache

# ---------------------------------------------------------------------------
# Starter-code templates per input pattern. {task} is the problem's todo hint.
# ---------------------------------------------------------------------------
IO_TEMPLATES: dict[str, dict[str, str]] = {
    "int": {
        "python": "n = int(input())\n\n# {task}\n",
        "javascript": "const n = Number(require('fs').readFileSync(0, 'utf8').trim());\n\n// {task}\n",
        "java": "import java.util.*;\npublic class Main {{\n  public static void main(String[] args) {{\n    long n = new Scanner(System.in).nextLong();\n    // {task}\n  }}\n}}\n",
        "cpp": "#include <bits/stdc++.h>\nusing namespace std;\nint main() {{\n  long long n; cin >> n;\n  // {task}\n  return 0;\n}}\n",
    },
    "ints": {
        "python": "nums = list(map(int, input().split()))\n\n# {task}\n",
        "javascript": "const nums = require('fs').readFileSync(0, 'utf8').trim().split(/\\s+/).map(Number);\n\n// {task}\n",
        "java": "import java.util.*;\npublic class Main {{\n  public static void main(String[] args) {{\n    Scanner sc = new Scanner(System.in);\n    List<Long> nums = new ArrayList<>();\n    while (sc.hasNextLong()) nums.add(sc.nextLong());\n    // {task}\n  }}\n}}\n",
        "cpp": "#include <bits/stdc++.h>\nusing namespace std;\nint main() {{\n  vector<long long> nums; long long x;\n  while (cin >> x) nums.push_back(x);\n  // {task}\n  return 0;\n}}\n",
    },
    "ints_int": {
        "python": "nums = list(map(int, input().split()))\nk = int(input())\n\n# {task}\n",
        "javascript": "const lines = require('fs').readFileSync(0, 'utf8').trim().split('\\n');\nconst nums = lines[0].trim().split(/\\s+/).map(Number);\nconst k = Number(lines[1]);\n\n// {task}\n",
        "java": "import java.util.*;\npublic class Main {{\n  public static void main(String[] args) {{\n    Scanner sc = new Scanner(System.in);\n    long[] nums = Arrays.stream(sc.nextLine().trim().split(\"\\\\s+\")).mapToLong(Long::parseLong).toArray();\n    long k = Long.parseLong(sc.nextLine().trim());\n    // {task}\n  }}\n}}\n",
        "cpp": "#include <bits/stdc++.h>\nusing namespace std;\nint main() {{\n  string line; getline(cin, line);\n  istringstream iss(line); vector<long long> nums; long long x;\n  while (iss >> x) nums.push_back(x);\n  long long k; cin >> k;\n  // {task}\n  return 0;\n}}\n",
    },
    "ints_ints": {
        "python": "a = list(map(int, input().split()))\nb = list(map(int, input().split()))\n\n# {task}\n",
        "javascript": "const lines = require('fs').readFileSync(0, 'utf8').trim().split('\\n');\nconst a = lines[0].trim().split(/\\s+/).map(Number);\nconst b = lines[1].trim().split(/\\s+/).map(Number);\n\n// {task}\n",
        "java": "import java.util.*;\npublic class Main {{\n  public static void main(String[] args) {{\n    Scanner sc = new Scanner(System.in);\n    long[] a = Arrays.stream(sc.nextLine().trim().split(\"\\\\s+\")).mapToLong(Long::parseLong).toArray();\n    long[] b = Arrays.stream(sc.nextLine().trim().split(\"\\\\s+\")).mapToLong(Long::parseLong).toArray();\n    // {task}\n  }}\n}}\n",
        "cpp": "#include <bits/stdc++.h>\nusing namespace std;\nvector<long long> readLine() {{\n  string line; getline(cin, line);\n  istringstream iss(line); vector<long long> v; long long x;\n  while (iss >> x) v.push_back(x);\n  return v;\n}}\nint main() {{\n  vector<long long> a = readLine(), b = readLine();\n  // {task}\n  return 0;\n}}\n",
    },
    "str": {
        "python": "s = input().strip()\n\n# {task}\n",
        "javascript": "const s = require('fs').readFileSync(0, 'utf8').trim();\n\n// {task}\n",
        "java": "import java.util.*;\npublic class Main {{\n  public static void main(String[] args) {{\n    String s = new Scanner(System.in).nextLine().trim();\n    // {task}\n  }}\n}}\n",
        "cpp": "#include <bits/stdc++.h>\nusing namespace std;\nint main() {{\n  string s; getline(cin, s);\n  // {task}\n  return 0;\n}}\n",
    },
    "two_strs": {
        "python": "s = input().strip()\nt = input().strip()\n\n# {task}\n",
        "javascript": "const lines = require('fs').readFileSync(0, 'utf8').split('\\n');\nconst s = lines[0].trim(), t = (lines[1] || '').trim();\n\n// {task}\n",
        "java": "import java.util.*;\npublic class Main {{\n  public static void main(String[] args) {{\n    Scanner sc = new Scanner(System.in);\n    String s = sc.nextLine().trim(), t = sc.nextLine().trim();\n    // {task}\n  }}\n}}\n",
        "cpp": "#include <bits/stdc++.h>\nusing namespace std;\nint main() {{\n  string s, t; getline(cin, s); getline(cin, t);\n  // {task}\n  return 0;\n}}\n",
    },
}


def _parse_ints(line: str) -> list[int]:
    return [int(x) for x in line.split()]


def _p(title, slug, difficulty, topic, description, io, task, solve, tests):
    return {
        "title": title, "slug": slug, "difficulty": difficulty, "topic": topic,
        "description": description, "io": io, "task": task, "solve": solve, "tests": tests,
    }


# ---------------------------------------------------------------------------
# Reference solutions
# ---------------------------------------------------------------------------
def _fizzbuzz(inp):
    n = int(inp)
    return "\n".join("FizzBuzz" if i % 15 == 0 else "Fizz" if i % 3 == 0 else "Buzz" if i % 5 == 0 else str(i) for i in range(1, n + 1))


def _fib(inp):
    n = int(inp)
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return str(a)


def _roman(inp):
    values = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    s = inp.strip()
    total = 0
    for i, ch in enumerate(s):
        v = values[ch]
        total += -v if i + 1 < len(s) and values[s[i + 1]] > v else v
    return str(total)


def _stock(inp):
    prices = _parse_ints(inp)
    best, lowest = 0, prices[0]
    for p in prices[1:]:
        best = max(best, p - lowest)
        lowest = min(lowest, p)
    return str(best)


def _three_sum_closest(inp):
    lines = inp.split("\n")
    nums, target = sorted(_parse_ints(lines[0])), int(lines[1])
    best = nums[0] + nums[1] + nums[2]
    for i in range(len(nums) - 2):
        lo, hi = i + 1, len(nums) - 1
        while lo < hi:
            s = nums[i] + nums[lo] + nums[hi]
            if abs(s - target) < abs(best - target):
                best = s
            if s < target:
                lo += 1
            elif s > target:
                hi -= 1
            else:
                return str(s)
    return str(best)


def _top_k_frequent(inp):
    lines = inp.split("\n")
    nums, k = _parse_ints(lines[0]), int(lines[1])
    freq = Counter(nums)
    ranked = sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))
    return " ".join(str(v) for v, _ in ranked[:k])


def _compress(inp):
    s = inp.strip()
    out, i = [], 0
    while i < len(s):
        j = i
        while j < len(s) and s[j] == s[i]:
            j += 1
        out.append(f"{s[i]}{j - i}")
        i = j
    return "".join(out)


def _longest_pal_len(inp):
    s = inp.strip()
    best = 0
    for center in range(2 * len(s) - 1):
        lo, hi = center // 2, center // 2 + center % 2
        while lo >= 0 and hi < len(s) and s[lo] == s[hi]:
            lo -= 1
            hi += 1
        best = max(best, hi - lo - 1)
    return str(best)


def _search_rotated(inp):
    lines = inp.split("\n")
    nums, target = _parse_ints(lines[0]), int(lines[1])
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return str(mid)
        if nums[lo] <= nums[mid]:
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return "-1"


def _subarray_sum_k(inp):
    lines = inp.split("\n")
    nums, k = _parse_ints(lines[0]), int(lines[1])
    seen = defaultdict(int)
    seen[0] = 1
    total = count = 0
    for x in nums:
        total += x
        count += seen[total - k]
        seen[total] += 1
    return str(count)


def _longest_consecutive(inp):
    nums = set(_parse_ints(inp))
    best = 0
    for x in nums:
        if x - 1 not in nums:
            y = x
            while y + 1 in nums:
                y += 1
            best = max(best, y - x + 1)
    return str(best)


def _gas_station(inp):
    lines = inp.split("\n")
    gas, cost = _parse_ints(lines[0]), _parse_ints(lines[1])
    if sum(gas) < sum(cost):
        return "-1"
    start = tank = 0
    for i in range(len(gas)):
        tank += gas[i] - cost[i]
        if tank < 0:
            start, tank = i + 1, 0
    return str(start)


def _daily_temps(inp):
    temps = _parse_ints(inp)
    result = [0] * len(temps)
    stack: list[int] = []
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:
            j = stack.pop()
            result[j] = i - j
        stack.append(i)
    return " ".join(map(str, result))


def _next_greater(inp):
    nums = _parse_ints(inp)
    result = [-1] * len(nums)
    stack: list[int] = []
    for i, x in enumerate(nums):
        while stack and nums[stack[-1]] < x:
            result[stack.pop()] = x
        stack.append(i)
    return " ".join(map(str, result))


def _decode_ways(inp):
    s = inp.strip()
    if not s or s[0] == "0":
        return "0"
    a, b = 1, 1  # ways up to i-2, i-1
    for i in range(1, len(s)):
        cur = 0
        if s[i] != "0":
            cur += b
        if 10 <= int(s[i - 1 : i + 1]) <= 26:
            cur += a
        a, b = b, cur
    return str(b)


def _coin_change_ii(inp):
    lines = inp.split("\n")
    coins, amount = _parse_ints(lines[0]), int(lines[1])
    dp = [0] * (amount + 1)
    dp[0] = 1
    for c in coins:
        for v in range(c, amount + 1):
            dp[v] += dp[v - c]
    return str(dp[amount])


def _word_break(inp):
    lines = inp.split("\n")
    s, words = lines[0].strip(), set(lines[1].split())
    dp = [True] + [False] * len(s)
    for i in range(1, len(s) + 1):
        dp[i] = any(dp[j] and s[j:i] in words for j in range(i))
    return "true" if dp[len(s)] else "false"


def _lis(inp):
    import bisect

    tails: list[int] = []
    for x in _parse_ints(inp):
        pos = bisect.bisect_left(tails, x)
        if pos == len(tails):
            tails.append(x)
        else:
            tails[pos] = x
    return str(len(tails))


def _partition_equal(inp):
    nums = _parse_ints(inp)
    total = sum(nums)
    if total % 2:
        return "false"
    target = total // 2
    reachable = {0}
    for x in nums:
        reachable |= {r + x for r in reachable if r + x <= target}
        if target in reachable:
            return "true"
    return "false"


def _find_duplicates(inp):
    counts = Counter(_parse_ints(inp))
    dups = sorted(v for v, c in counts.items() if c >= 2)
    return " ".join(map(str, dups)) if dups else "-1"


def _trap_water(inp):
    h = _parse_ints(inp)
    lo, hi = 0, len(h) - 1
    left_max = right_max = water = 0
    while lo < hi:
        if h[lo] < h[hi]:
            left_max = max(left_max, h[lo])
            water += left_max - h[lo]
            lo += 1
        else:
            right_max = max(right_max, h[hi])
            water += right_max - h[hi]
            hi -= 1
    return str(water)


def _median_sorted(inp):
    lines = inp.split("\n")
    merged = sorted(_parse_ints(lines[0]) + _parse_ints(lines[1]))
    n = len(merged)
    median = merged[n // 2] if n % 2 else (merged[n // 2 - 1] + merged[n // 2]) / 2
    return f"{float(median):.1f}"


def _longest_valid_parens(inp):
    s = inp.strip()
    stack = [-1]
    best = 0
    for i, ch in enumerate(s):
        if ch == "(":
            stack.append(i)
        else:
            stack.pop()
            if not stack:
                stack.append(i)
            else:
                best = max(best, i - stack[-1])
    return str(best)


def _edit_distance(inp):
    lines = inp.split("\n")
    a, b = lines[0].strip(), lines[1].strip()
    dp = list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        prev, dp[0] = dp[0], i
        for j in range(1, len(b) + 1):
            cur = dp[j]
            dp[j] = prev if a[i - 1] == b[j - 1] else 1 + min(prev, dp[j], dp[j - 1])
            prev = cur
    return str(dp[len(b)])


def _n_queens(inp):
    n = int(inp)

    def solve(row, cols, diag1, diag2):
        if row == n:
            return 1
        count = 0
        for col in range(n):
            if col in cols or row + col in diag1 or row - col in diag2:
                continue
            count += solve(row + 1, cols | {col}, diag1 | {row + col}, diag2 | {row - col})
        return count

    return str(solve(0, set(), set(), set()))


def _largest_rectangle(inp):
    heights = _parse_ints(inp) + [0]
    stack: list[int] = []
    best = 0
    for i, h in enumerate(heights):
        while stack and heights[stack[-1]] >= h:
            height = heights[stack.pop()]
            width = i if not stack else i - stack[-1] - 1
            best = max(best, height * width)
        stack.append(i)
    return str(best)


def _min_window(inp):
    lines = inp.split("\n")
    s, t = lines[0].strip(), lines[1].strip()
    need = Counter(t)
    missing = len(t)
    best = (0, len(s) + 1)
    lo = 0
    for hi, ch in enumerate(s, 1):
        if need[ch] > 0:
            missing -= 1
        need[ch] -= 1
        if missing == 0:
            while need[s[lo]] < 0:
                need[s[lo]] += 1
                lo += 1
            if hi - lo < best[1] - best[0]:
                best = (lo, hi)
    return s[best[0]:best[1]] if best[1] <= len(s) else "-1"


def _sliding_max(inp):
    lines = inp.split("\n")
    nums, k = _parse_ints(lines[0]), int(lines[1])
    dq: deque[int] = deque()
    out = []
    for i, x in enumerate(nums):
        while dq and nums[dq[-1]] <= x:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            out.append(nums[dq[0]])
    return " ".join(map(str, out))


def _burst_balloons(inp):
    nums = [1] + _parse_ints(inp) + [1]

    @lru_cache(maxsize=None)
    def best(lo, hi):  # open interval (lo, hi)
        if lo + 1 == hi:
            return 0
        return max(
            best(lo, k) + nums[lo] * nums[k] * nums[hi] + best(k, hi)
            for k in range(lo + 1, hi)
        )

    result = best(0, len(nums) - 1)
    best.cache_clear()
    return str(result)


def _count_smaller(inp):
    nums = _parse_ints(inp)
    out = [sum(1 for y in nums[i + 1:] if y < x) for i, x in enumerate(nums)]
    return " ".join(map(str, out))


def _lcp(inp):
    words = inp.split()
    prefix = words[0]
    for w in words[1:]:
        while not w.startswith(prefix):
            prefix = prefix[:-1]
            if not prefix:
                return "-1"
    return prefix


# ---------------------------------------------------------------------------
# The bank
# ---------------------------------------------------------------------------
BANK: list[dict] = [
    # ---------------- EASY ----------------
    _p("Reverse String", "reverse-string", "easy", "strings",
       "Print the input string reversed.\n\n**Example**: `hello` → `olleh`",
       "str", "print the reversed string",
       lambda s: s.strip()[::-1],
       ["hello", "InterviewPilot", "a", "racecar x"]),
    _p("Palindrome Check", "palindrome-check", "easy", "strings",
       "Print `true` if the string reads the same forwards and backwards, else `false`.\n\n**Example**: `racecar` → `true`",
       "str", "print 'true' or 'false'",
       lambda s: "true" if s.strip() == s.strip()[::-1] else "false",
       ["racecar", "hello", "ab", "abcba"]),
    _p("FizzBuzz", "fizzbuzz", "easy", "math",
       "Given n, print numbers 1..n one per line — but print `Fizz` for multiples of 3, `Buzz` for multiples of 5, `FizzBuzz` for both.",
       "int", "print FizzBuzz lines for 1..n",
       _fizzbuzz, ["5", "15", "1", "16"]),
    _p("Sum of Digits", "sum-of-digits", "easy", "math",
       "Print the sum of the digits of a non-negative integer.\n\n**Example**: `12345` → `15`",
       "int", "print the digit sum",
       lambda s: str(sum(int(d) for d in s.strip())), ["12345", "0", "999999", "10203"]),
    _p("Factorial", "factorial", "easy", "math",
       "Print n! (n ≤ 20).\n\n**Example**: `5` → `120`",
       "int", "print n factorial",
       lambda s: str(math.factorial(int(s))), ["5", "0", "1", "12"]),
    _p("Nth Fibonacci", "nth-fibonacci", "easy", "dynamic programming",
       "Print the n-th Fibonacci number where F(0)=0, F(1)=1 (n ≤ 80).\n\n**Example**: `10` → `55`",
       "int", "print F(n)",
       _fib, ["10", "0", "1", "40"]),
    _p("Count Vowels", "count-vowels", "easy", "strings",
       "Print how many vowels (a, e, i, o, u — case-insensitive) the string contains.\n\n**Example**: `programming` → `3`",
       "str", "print the vowel count",
       lambda s: str(sum(1 for c in s.strip().lower() if c in "aeiou")),
       ["programming", "AEIOU", "xyz", "Interview Pilot"]),
    _p("Max and Min", "max-and-min", "easy", "arrays",
       "Print the maximum and minimum of the list, space-separated.\n\n**Example**: `3 1 4 1 5` → `5 1`",
       "ints", "print 'max min'",
       lambda s: f"{max(_parse_ints(s))} {min(_parse_ints(s))}",
       ["3 1 4 1 5", "7", "-5 -2 -9", "0 100 -100"]),
    _p("Contains Duplicate", "contains-duplicate", "easy", "hashing",
       "Print `true` if any value appears at least twice, else `false`.\n\n**Example**: `1 2 3 1` → `true`",
       "ints", "print 'true' or 'false'",
       lambda s: "true" if len(set(_parse_ints(s))) < len(_parse_ints(s)) else "false",
       ["1 2 3 1", "1 2 3 4", "1 1 1 3 3 4 3 2 4 2", "99"]),
    _p("Missing Number", "missing-number", "easy", "math",
       "The list contains n distinct numbers from 0..n with exactly one missing. Print the missing number.\n\n**Example**: `3 0 1` → `2`",
       "ints", "print the missing number",
       lambda s: str(len(_parse_ints(s)) * (len(_parse_ints(s)) + 1) // 2 - sum(_parse_ints(s))),
       ["3 0 1", "0 1", "9 6 4 2 3 5 7 0 1", "0"]),
    _p("Single Number", "single-number", "easy", "bit manipulation",
       "Every element appears twice except one. Print the one that appears once. Aim for O(n) time, O(1) space.\n\n**Example**: `4 1 2 1 2` → `4`",
       "ints", "print the single number",
       lambda s: str(__import__('functools').reduce(lambda a, b: a ^ b, _parse_ints(s))),
       ["4 1 2 1 2", "2 2 1", "1", "7 3 7 9 3"]),
    _p("Move Zeroes", "move-zeroes", "easy", "two pointers",
       "Move all zeroes to the end while keeping the relative order of non-zero elements. Print the result space-separated.\n\n**Example**: `0 1 0 3 12` → `1 3 12 0 0`",
       "ints", "print the array with zeroes moved to the end",
       lambda s: " ".join(map(str, [x for x in _parse_ints(s) if x != 0] + [0] * _parse_ints(s).count(0))),
       ["0 1 0 3 12", "0", "1 2 3", "0 0 1"]),
    _p("Squares of a Sorted Array", "sorted-squares", "easy", "two pointers",
       "Given a sorted list (may contain negatives), print the squares in sorted order.\n\n**Example**: `-4 -1 0 3 10` → `0 1 9 16 100`",
       "ints", "print the sorted squares",
       lambda s: " ".join(map(str, sorted(x * x for x in _parse_ints(s)))),
       ["-4 -1 0 3 10", "-7 -3 2 3 11", "1 2 3", "-5"]),
    _p("Best Time to Buy and Sell Stock", "stock-buy-sell", "easy", "arrays",
       "Given daily prices, print the max profit from one buy + one later sell (0 if no profit possible).\n\n**Example**: `7 1 5 3 6 4` → `5`",
       "ints", "print the max profit",
       _stock, ["7 1 5 3 6 4", "7 6 4 3 1", "2 10", "5"]),
    _p("Roman to Integer", "roman-to-integer", "easy", "strings",
       "Convert a Roman numeral (I V X L C D M) to an integer.\n\n**Example**: `MCMXCIV` → `1994`",
       "str", "print the integer value",
       _roman, ["MCMXCIV", "III", "LVIII", "XL"]),
    _p("First Unique Character", "first-unique-char", "easy", "hashing",
       "Print the index (0-based) of the first non-repeating character, or `-1` if none.\n\n**Example**: `leetcode` → `0`",
       "str", "print the index or -1",
       lambda s: str(next((i for i, c in enumerate(s.strip()) if Counter(s.strip())[c] == 1), -1)),
       ["leetcode", "loveleetcode", "aabb", "z"]),
    _p("Majority Element", "majority-element", "easy", "arrays",
       "Print the element that appears more than n/2 times (guaranteed to exist).\n\n**Example**: `2 2 1 1 1 2 2` → `2`",
       "ints", "print the majority element",
       lambda s: str(Counter(_parse_ints(s)).most_common(1)[0][0]),
       ["2 2 1 1 1 2 2", "3 2 3", "1", "5 5 5 1 2"]),

    # ---------------- MEDIUM ----------------
    _p("Longest Common Prefix", "longest-common-prefix", "medium", "strings",
       "Given space-separated words, print their longest common prefix, or `-1` if there is none.\n\n**Example**: `flower flow flight` → `fl`",
       "str", "print the longest common prefix or -1",
       _lcp, ["flower flow flight", "dog racecar car", "interview interviewer interviews", "same same"]),
    _p("3Sum Closest", "three-sum-closest", "medium", "two pointers",
       "Line 1: integers. Line 2: target. Print the sum of the three numbers closest to the target.\n\n**Example**: `-1 2 1 -4`, target `1` → `2`",
       "ints_int", "print the closest triple sum",
       _three_sum_closest, ["-1 2 1 -4\n1", "0 0 0\n1", "1 1 1 0\n-100", "4 0 5 -5 3 3 0 -4 -5\n-2"]),
    _p("Container With Most Water", "container-most-water", "medium", "two pointers",
       "Heights of vertical lines. Print the max water area between any two lines.\n\n**Example**: `1 8 6 2 5 4 8 3 7` → `49`",
       "ints", "print the max area",
       lambda s: _container(s),
       ["1 8 6 2 5 4 8 3 7", "1 1", "4 3 2 1 4", "1 2 1"]),
    _p("Sort Colors", "sort-colors", "medium", "sorting",
       "Sort an array of 0s, 1s and 2s in one pass (Dutch national flag). Print the sorted array.\n\n**Example**: `2 0 2 1 1 0` → `0 0 1 1 2 2`",
       "ints", "print the sorted 0/1/2 array",
       lambda s: " ".join(map(str, sorted(_parse_ints(s)))),
       ["2 0 2 1 1 0", "2 0 1", "0", "1 1 1"]),
    _p("Kth Largest Element", "kth-largest", "medium", "heaps",
       "Line 1: integers. Line 2: k. Print the k-th largest element.\n\n**Example**: `3 2 1 5 6 4`, k=`2` → `5`",
       "ints_int", "print the kth largest",
       lambda s: str(sorted(_parse_ints(s.split("\n")[0]), reverse=True)[int(s.split("\n")[1]) - 1]),
       ["3 2 1 5 6 4\n2", "3 2 3 1 2 4 5 5 6\n4", "1\n1", "7 7 7 7\n3"]),
    _p("Top K Frequent Elements", "top-k-frequent", "medium", "heaps",
       "Line 1: integers. Line 2: k. Print the k most frequent values, most-frequent first (ties: smaller value first).\n\n**Example**: `1 1 1 2 2 3`, k=`2` → `1 2`",
       "ints_int", "print k most frequent values",
       _top_k_frequent, ["1 1 1 2 2 3\n2", "1\n1", "4 4 4 6 6 5\n3", "9 9 8 8 7\n2"]),
    _p("Longest Palindromic Substring (Length)", "longest-palindrome-length", "medium", "strings",
       "Print the LENGTH of the longest palindromic substring.\n\n**Example**: `babad` → `3`",
       "str", "print the length",
       _longest_pal_len, ["babad", "cbbd", "abcde", "forgeeksskeegfor"]),
    _p("String Compression", "string-compression", "medium", "strings",
       "Compress runs of repeated characters as char+count.\n\n**Example**: `aaabb` → `a3b2`",
       "str", "print the compressed string",
       _compress, ["aaabb", "abc", "zzzzzzzzzzzz", "aabbaa"]),
    _p("Rotate Array", "rotate-array", "medium", "arrays",
       "Line 1: integers. Line 2: k. Rotate the array to the RIGHT by k steps and print it.\n\n**Example**: `1 2 3 4 5 6 7`, k=`3` → `5 6 7 1 2 3 4`",
       "ints_int", "print the rotated array",
       lambda s: (lambda nums, k: " ".join(map(str, nums[-k % len(nums):] + nums[:-k % len(nums)])) if k % len(nums) else " ".join(map(str, nums)))(_parse_ints(s.split("\n")[0]), int(s.split("\n")[1])),
       ["1 2 3 4 5 6 7\n3", "-1 -100 3 99\n2", "1 2\n4", "5\n1"]),
    _p("Search in Rotated Sorted Array", "search-rotated", "medium", "binary search",
       "Line 1: a sorted array rotated at an unknown pivot. Line 2: target. Print its index or `-1`. O(log n) required.\n\n**Example**: `4 5 6 7 0 1 2`, target `0` → `4`",
       "ints_int", "print the index or -1",
       _search_rotated, ["4 5 6 7 0 1 2\n0", "4 5 6 7 0 1 2\n3", "1\n1", "5 1 3\n3"]),
    _p("Subarray Sum Equals K", "subarray-sum-k", "medium", "hashing",
       "Line 1: integers. Line 2: k. Print how many contiguous subarrays sum to exactly k.\n\n**Example**: `1 1 1`, k=`2` → `2`",
       "ints_int", "print the count of subarrays",
       _subarray_sum_k, ["1 1 1\n2", "1 2 3\n3", "1 -1 0\n0", "3 4 7 2 -3 1 4 2\n7"]),
    _p("Longest Consecutive Sequence", "longest-consecutive", "medium", "hashing",
       "Print the length of the longest run of consecutive integers present (order doesn't matter). O(n) expected.\n\n**Example**: `100 4 200 1 3 2` → `4`",
       "ints", "print the longest streak length",
       _longest_consecutive, ["100 4 200 1 3 2", "0 3 7 2 5 8 4 6 0 1", "9", "10 5 12 3 55 30 4 11 2"]),
    _p("Jump Game", "jump-game", "medium", "greedy",
       "Each value is your max jump length from that index. Print `true` if you can reach the last index from the first.\n\n**Example**: `2 3 1 1 4` → `true`",
       "ints", "print 'true' or 'false'",
       lambda s: _jump_game(s),
       ["2 3 1 1 4", "3 2 1 0 4", "0", "2 0 0"]),
    _p("Gas Station", "gas-station", "medium", "greedy",
       "Line 1: gas at each station. Line 2: cost to travel to the next. Print the starting station index that completes the circuit, or `-1`.\n\n**Example**: gas `1 2 3 4 5`, cost `3 4 5 1 2` → `3`",
       "ints_ints", "print the start index or -1",
       _gas_station, ["1 2 3 4 5\n3 4 5 1 2", "2 3 4\n3 4 3", "5\n4", "3 1 1\n1 2 2"]),
    _p("Daily Temperatures", "daily-temperatures", "medium", "stacks",
       "For each day, print how many days you'd wait for a warmer temperature (0 if never), space-separated.\n\n**Example**: `73 74 75 71 69 72 76 73` → `1 1 4 2 1 1 0 0`",
       "ints", "print the wait days for each index",
       _daily_temps, ["73 74 75 71 69 72 76 73", "30 40 50 60", "30 60 90", "90 80 70"]),
    _p("Next Greater Element", "next-greater-element", "medium", "stacks",
       "For each element, print the first greater element to its right (`-1` if none), space-separated.\n\n**Example**: `2 1 2 4 3` → `4 2 4 -1 -1`",
       "ints", "print next greater for each element",
       _next_greater, ["2 1 2 4 3", "5 4 3 2 1", "1 2 3", "7"]),
    _p("Decode Ways", "decode-ways", "medium", "dynamic programming",
       "A digit string decodes with A=1..Z=26. Print how many ways it can be decoded.\n\n**Example**: `226` → `3`",
       "str", "print the number of decodings",
       _decode_ways, ["226", "12", "06", "11106"]),
    _p("Unique Paths", "unique-paths", "medium", "dynamic programming",
       "Input: `m n` (grid rows, cols). A robot walks from top-left to bottom-right moving only right/down. Print the number of unique paths.\n\n**Example**: `3 7` → `28`",
       "ints", "print the number of paths",
       lambda s: str(math.comb(sum(_parse_ints(s)) - 2, _parse_ints(s)[0] - 1)),
       ["3 7", "3 2", "1 1", "10 10"]),
    _p("Coin Change II", "coin-change-ii", "medium", "dynamic programming",
       "Line 1: coin denominations. Line 2: amount. Print the number of COMBINATIONS that make the amount.\n\n**Example**: coins `1 2 5`, amount `5` → `4`",
       "ints_int", "print the number of combinations",
       _coin_change_ii, ["1 2 5\n5", "2\n3", "10\n10", "1 2 3\n8"]),
    _p("House Robber", "house-robber", "medium", "dynamic programming",
       "You can't rob two adjacent houses. Print the max total you can rob.\n\n**Example**: `2 7 9 3 1` → `12`",
       "ints", "print the max loot",
       lambda s: str(__import__('functools').reduce(lambda ab, x: (ab[1], max(ab[1], ab[0] + x)), _parse_ints(s), (0, 0))[1]),
       ["2 7 9 3 1", "1 2 3 1", "5", "100 1 1 100"]),
    _p("Word Break", "word-break", "medium", "dynamic programming",
       "Line 1: string s. Line 2: dictionary words (space-separated). Print `true` if s can be segmented into dictionary words.\n\n**Example**: `leetcode` + `leet code` → `true`",
       "two_strs", "print 'true' or 'false'",
       _word_break, ["leetcode\nleet code", "applepenapple\napple pen", "catsandog\ncats dog sand and cat", "a\nb"]),
    _p("Longest Increasing Subsequence", "longest-increasing-subsequence", "medium", "dynamic programming",
       "Print the length of the longest strictly increasing subsequence. O(n log n) earns full marks.\n\n**Example**: `10 9 2 5 3 7 101 18` → `4`",
       "ints", "print the LIS length",
       _lis, ["10 9 2 5 3 7 101 18", "0 1 0 3 2 3", "7 7 7 7", "1 3 6 7 9 4 10 5 6"]),
    _p("Partition Equal Subset Sum", "partition-equal-subset", "medium", "dynamic programming",
       "Print `true` if the list can be split into two subsets with equal sums.\n\n**Example**: `1 5 11 5` → `true`",
       "ints", "print 'true' or 'false'",
       _partition_equal, ["1 5 11 5", "1 2 3 5", "2 2", "1 1 1 1 2"]),
    _p("Find All Duplicates", "find-all-duplicates", "medium", "hashing",
       "Print every value that appears at least twice, sorted ascending, space-separated — or `-1` if none.\n\n**Example**: `4 3 2 7 8 2 3 1` → `2 3`",
       "ints", "print duplicates sorted, or -1",
       _find_duplicates, ["4 3 2 7 8 2 3 1", "1 1 2", "1 2 3", "5 5 5 5"]),

    # ---------------- HARD ----------------
    _p("Trapping Rain Water", "trapping-rain-water", "hard", "two pointers",
       "Elevation heights. Print how much water is trapped after raining.\n\n**Example**: `0 1 0 2 1 0 1 3 2 1 2 1` → `6`",
       "ints", "print trapped water units",
       _trap_water, ["0 1 0 2 1 0 1 3 2 1 2 1", "4 2 0 3 2 5", "1 2 3", "5 0 5 0 5"]),
    _p("Median of Two Sorted Arrays", "median-two-sorted", "hard", "binary search",
       "Two lines, each a sorted array. Print the median of the merged data with ONE decimal place.\n\n**Example**: `1 3` + `2` → `2.0`",
       "ints_ints", "print the median with one decimal",
       _median_sorted, ["1 3\n2", "1 2\n3 4", "0 0\n0 0", "2\n1 3 4 5 6"]),
    _p("Longest Valid Parentheses", "longest-valid-parentheses", "hard", "stacks",
       "Print the length of the longest valid (well-formed) parentheses substring.\n\n**Example**: `)()())` → `4`",
       "str", "print the max valid length",
       _longest_valid_parens, [")()())", "(()", "()(())", "((((("]),
    _p("Edit Distance", "edit-distance", "hard", "dynamic programming",
       "Two lines: words a and b. Print the minimum number of insert/delete/replace operations to turn a into b.\n\n**Example**: `horse` → `ros` = `3`",
       "two_strs", "print the edit distance",
       _edit_distance, ["horse\nros", "intention\nexecution", "abc\nabc", "abc\nxyz"]),
    _p("N-Queens Count", "n-queens-count", "hard", "backtracking",
       "Print the number of distinct ways to place n non-attacking queens on an n×n board (n ≤ 9).\n\n**Example**: `4` → `2`",
       "int", "print the number of solutions",
       _n_queens, ["4", "1", "8", "6"]),
    _p("Largest Rectangle in Histogram", "largest-rectangle-histogram", "hard", "stacks",
       "Bar heights (width 1 each). Print the area of the largest rectangle that fits inside the histogram.\n\n**Example**: `2 1 5 6 2 3` → `10`",
       "ints", "print the max rectangle area",
       _largest_rectangle, ["2 1 5 6 2 3", "2 4", "1 1 1 1", "6 2 5 4 5 1 6"]),
    _p("Minimum Window Substring", "min-window-substring", "hard", "sliding window",
       "Line 1: s. Line 2: t. Print the smallest substring of s containing every character of t (with multiplicity), or `-1`.\n\n**Example**: `ADOBECODEBANC` + `ABC` → `BANC`",
       "two_strs", "print the min window or -1",
       _min_window, ["ADOBECODEBANC\nABC", "a\na", "a\naa", "ab\nb"]),
    _p("Sliding Window Maximum", "sliding-window-maximum", "hard", "sliding window",
       "Line 1: integers. Line 2: window size k. Print the max of each window, space-separated. O(n) expected.\n\n**Example**: `1 3 -1 -3 5 3 6 7`, k=`3` → `3 3 5 5 6 7`",
       "ints_int", "print each window's max",
       _sliding_max, ["1 3 -1 -3 5 3 6 7\n3", "1\n1", "9 8 7 6\n2", "4 -2 7 3 3 3\n3"]),
    _p("Burst Balloons", "burst-balloons", "hard", "dynamic programming",
       "Bursting balloon i earns nums[left]*nums[i]*nums[right] (out-of-bounds counts as 1). Print the max coins from bursting all balloons.\n\n**Example**: `3 1 5 8` → `167`",
       "ints", "print the max coins",
       _burst_balloons, ["3 1 5 8", "1 5", "7", "9 76 64 21"]),
    _p("Count of Smaller Numbers After Self", "count-smaller-after-self", "hard", "sorting",
       "For each element, print how many elements to its RIGHT are smaller, space-separated.\n\n**Example**: `5 2 6 1` → `2 1 1 0`",
       "ints", "print counts for each index",
       _count_smaller, ["5 2 6 1", "-1 -1", "3 2 1", "1 2 3 4"]),
]


def _container(inp):
    h = _parse_ints(inp)
    lo, hi = 0, len(h) - 1
    best = 0
    while lo < hi:
        best = max(best, min(h[lo], h[hi]) * (hi - lo))
        if h[lo] < h[hi]:
            lo += 1
        else:
            hi -= 1
    return str(best)


def _jump_game(inp):
    nums = _parse_ints(inp)
    reach = 0
    for i, x in enumerate(nums):
        if i > reach:
            return "false"
        reach = max(reach, i + x)
    return "true"


def bank_problems() -> list[dict]:
    """Materialize the bank into seed-ready problem dicts (expected outputs
    computed from the reference solutions; first 2 tests visible, rest hidden)."""
    out = []
    for p in BANK:
        cases = [{"input": t, "expected": p["solve"](t)} for t in p["tests"]]
        starter = {
            lang: template.format(task=p["task"])
            for lang, template in IO_TEMPLATES[p["io"]].items()
        }
        out.append({
            "title": p["title"], "slug": p["slug"], "difficulty": p["difficulty"],
            "topic": p["topic"], "description": p["description"], "starter": starter,
            "visible": cases[:2], "hidden": cases[2:],
        })
    return out
