#!/usr/bin/env bash
set -euo pipefail
state=.github/wow-version.json
toc=FriendlyNameplateGuild.toc
candidate=candidate.json
output() { if [[ -n ${GITHUB_OUTPUT:-} ]]; then printf '%s\n' "$1" >> "$GITHUB_OUTPUT"; else printf '%s\n' "$1"; fi; }
fail() { echo "$*" >&2; exit 1; }
fetch() { curl --fail --silent --show-error --location --retry 2 --max-time 30 --max-filesize 65536 --proto '=https' --proto-redir '=https' "$1"; }

case ${1:-} in
  detect)
    region=$(jq -er '.region' "$state")
    previous=$(jq -er '.build' "$state")
    known_patch=$(jq -er '.game_version' "$state")
    if [[ -n ${FNG_VERSION_FILE:-} ]]; then body=$(cat "$FNG_VERSION_FILE"); else body=$(fetch https://us.version.battle.net/v2/products/wowf/versions); fi
    row=$(printf '%s\n' "$body" | awk -F'|' -v region="$region" '
      NR == 1 { columns=NF; for(i=1;i<=NF;i++) { split($i,h,"!"); if(seen[h[1]]++) exit 2; if(h[1]=="Region") r=i; if(h[1]=="BuildId") b=i; if(h[1]=="VersionsName") v=i } }
      NR > 1 && r && $r == region { if(NF!=columns) exit 2; sub(/\r$/,"",$v); print $b "|" $v; count++ }
      END { if(!r || !b || !v || count!=1) exit 3 }') || fail 'Invalid Blizzard version table or missing/duplicate region'
    IFS='|' read -r build version <<< "$row"
    [[ $version =~ ^(1\.[0-9]{1,2}\.[0-9]{1,2})\.([1-9][0-9]{0,9})$ ]] || fail 'Invalid Forever version'
    patch=${BASH_REMATCH[1]}
    [[ $build == "${BASH_REMATCH[2]}" ]] || fail 'BuildId and VersionsName disagree'
    (( build >= previous )) || fail 'Refusing a regressing live build'
    [[ $build != "$previous" || $patch == "$known_patch" ]] || fail 'Conflicting metadata for the current build'
    output "build=$build"
    changed=false; if (( build > previous )); then changed=true; fi
    output "changed=$changed"
    interface=null
    if [[ $patch == "$known_patch" ]]; then
      interface=$(jq -er '.interface' "$state")
    elif [[ -n ${INTERFACE_FEED:-} ]]; then
      verified=$(fetch "$INTERFACE_FEED")
      jq -e --argjson build "$build" '.product=="wowf" and .channel=="live" and .build==$build and (.interface|type)=="number" and .interface>=16000 and .interface<17000 and (.interface|floor)==.interface' <<< "$verified" >/dev/null || fail 'Interface feed does not match the live build'
      interface=$(jq -er '.interface' <<< "$verified")
    fi
    jq -n --argjson build "$build" --arg patch "$patch" --argjson interface "$interface" '{build:$build,game_version:$patch,interface:$interface}' > "$candidate"
    cat "$candidate"
    ;;
  stage)
    build=$(jq -er '.build' "$candidate")
    interface=$(jq -er '.interface | select(type=="number" and .>=16000 and .<17000 and floor==.)' "$candidate") || fail 'New patch needs a verified Interface value; no Interface was guessed'
    previous=$(jq -er '.build' "$state")
    old_interface=$(jq -er '.interface' "$state")
    current=$(awk '/^## Interface:/ { print $3 }' "$toc" | tr -d '\r')
    [[ $current == "$old_interface" ]] || fail 'TOC and build checkpoint disagree'
    (( build >= previous && interface >= old_interface )) || fail 'Refusing a downgrade'
    if (( build == previous )); then [[ $interface == "$old_interface" ]] || fail 'Interface changed without a new build'; echo 'No new build'; exit 0; fi
    version=$(jq -er '.addon_version' "$state")
    [[ $version =~ ^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$ ]] || fail 'Invalid addon version'
    version="${BASH_REMATCH[1]}.${BASH_REMATCH[2]}.$((BASH_REMATCH[3]+1))"
    patch=$(jq -er '.game_version' "$candidate")
    jq --arg version "$version" --arg patch "$patch" --argjson build "$build" --argjson interface "$interface" '.addon_version=$version | .game_version=$patch | .build=$build | .interface=$interface' "$state" > "$state.tmp"
    mv "$state.tmp" "$state"
    sed -i -E "s/^## Interface: .*/## Interface: $interface/" "$toc"
    tag="v$version"
    if ! jq -e '.runtime_ready == true' "$state" >/dev/null; then tag+="-beta.1"; fi
    output "tag=$tag"
    ;;
  *) fail 'Usage: check-wow.sh detect|stage' ;;
esac
