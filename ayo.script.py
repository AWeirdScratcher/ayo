#!/usr/bin/python

import ayo

print(ayo.Template.convert_dict_to_list({
    "sus.py": "print('bruh...')",
    "among_us": {
        "suspicious.py": "wow",
        "more": {
            "stuff": {
                "sus.py": "so sus"
            }
        }
    }
}))