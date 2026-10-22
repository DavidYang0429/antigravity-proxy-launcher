#!/bin/zsh
cd -- "${0:A:h}" || exit 1
python_bin=$(command -v python3)
if [[ -z "$python_bin" ]]; then
 print '需要先安装 Python 3。'; read '?按回车关闭'; exit 1
fi
"$python_bin" tool.py install --dock
result=$?
if (( result != 0 )); then
 print '安装未完成，请查看上方原因。'
fi
read '?按回车关闭'
exit "$result"
