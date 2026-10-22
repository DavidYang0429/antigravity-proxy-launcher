#!/bin/zsh
proxy_settings=$(/usr/sbin/scutil --proxy)
proxy_host=$(print -r -- "$proxy_settings" | /usr/bin/awk '/HTTPSProxy :/ {print $3; exit}')
proxy_port=$(print -r -- "$proxy_settings" | /usr/bin/awk '/HTTPSPort :/ {print $3; exit}')
proxy_enabled=$(print -r -- "$proxy_settings" | /usr/bin/awk '/HTTPSEnable :/ {print $3; exit}')
if [[ "$proxy_enabled" != 1 || -z "$proxy_host" || -z "$proxy_port" ]]; then
 /usr/bin/osascript -e 'display alert "Antigravity 代理启动失败" message "请先在代理客户端开启系统代理，然后重试。"'
 exit 1
fi
export HTTP_PROXY="http://${proxy_host}:${proxy_port}"
export HTTPS_PROXY="$HTTP_PROXY"
export ALL_PROXY="$HTTP_PROXY"
export http_proxy="$HTTP_PROXY" https_proxy="$HTTP_PROXY" all_proxy="$HTTP_PROXY"
export NO_PROXY="localhost,127.0.0.1,::1"
export no_proxy="$NO_PROXY"
/Applications/Antigravity.app/Contents/MacOS/Antigravity "$@" &
wait $!
