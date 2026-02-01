#!/usr/bin/env bash
# Simple bash completion for `calendar` wrapper
_calendar()
{
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    opts="audit check list upload sync delete extract"
    if [[ ${COMP_CWORD} -eq 1 ]] ; then
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        return 0
    fi
}
complete -F _calendar calendar
