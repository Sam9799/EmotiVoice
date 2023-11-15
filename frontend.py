# Copyright 2023, YOUDAO
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
from pypinyin import pinyin, lazy_pinyin, Style
import jieba
import string

def split_py(py):
    tone = py[-1]
    py = py[:-1]
    sm = ""
    ym = ""
    suf_r = ""
    if py[-1] == 'r':
        suf_r = 'r'
        py = py[:-1]
    if py in ['zi', 'ci', 'si', 'ri']:
        sm = py[:1]
        ym = "ii"
    elif py in ['zhi', 'chi', 'shi']:
        sm = py[:2]
        ym = "iii"
    elif py in ['ya', 'yan', 'yang', 'yao', 'ye', 'yong', 'you']:
        sm = ""
        ym = f'i{py[1:]}'
    elif py in ['yi', 'yin', 'ying']:
        sm = ""
        ym = py[1:]
    elif py in ['yu', 'yv', 'yuan', 'yvan', 'yue ', 'yve', 'yun', 'yvn']:
        sm = ""
        ym = f'v{py[2:]}'
    elif py == 'wu':
        sm = ""
        ym = "u"
    elif py[0] == 'w':
        sm = ""
        ym = f"u{py[1:]}"
    elif len(py) >= 2 and py[0] in ['j', 'q', 'x'] and py[1] == 'u':
        sm = py[0]
        ym = f'v{py[2:]}'
    else:
        seg_pos = re.search('a|e|i|o|u|v', py)
        sm = py[:seg_pos.start()]
        ym = py[seg_pos.start():]
        if ym == 'ui':
            ym = 'uei'
        elif ym == 'iu':
            ym = 'iou'
        elif ym == 'un':
            ym = 'uen'
        elif ym == 'ue':
            ym = 've'
    ym += suf_r + tone
    return sm, ym


chinese_punctuation_pattern = r'[\u3002\uff0c\uff1f\uff01\uff1b\uff1a\u201c\u201d\u2018\u2019\u300a\u300b\u3008\u3009\u3010\u3011\u300e\u300f\u2014\u2026]'


def has_chinese_punctuation(text):
    match = re.search(chinese_punctuation_pattern, text)
    return match is not None
def has_english_punctuation(text):
    return text in string.punctuation

def g2p(text):
    res_text=["<sos/eos>"]
    seg_list = jieba.cut(text)
    for seg in seg_list:
        
        py =[_py[0] for _py in pinyin(seg, style=Style.TONE3,neutral_tone_with_five=True)]

        if any(has_chinese_punctuation(_py) for _py in py) or any(
            has_english_punctuation(_py) for _py in py
        ):
            res_text.pop()
            res_text.append("sp3")
        else:
            
            py = [" ".join(split_py(_py)) for _py in py]

            res_text.extend((" sp0 ".join(py), "sp1"))
    res_text.pop()
    res_text.append("<sos/eos>")
    return " ".join(res_text)

if __name__ == "__main__":
    import sys
    from os.path import isfile
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <text>")
        exit()
    text_file = sys.argv[1]
    if isfile(text_file):
        with open(text_file, 'r') as fp:
            for line in fp:
                phoneme=g2p(line.rstrip())
                print(phoneme)
