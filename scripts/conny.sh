CONNY_ENV_LOCATION=. # /mnt/s-ws/env
environment='scie4002'
function __conny_hashr() {
    if [ -n "${ZSH_VERSION:+x}" ]; then
        \rehash
    elif [ -n "${POSH_VERSION:+x}" ]; then
        :  # pass
    else
        \hash -r
    fi
}


function conny () {
    \local cmd="${1-__missing__}"
    case "${cmd}" in 
        activate)
            if [[ -v CONNY_OLD_PATH ]]; then
                echo -e '\033[31m\033[1mconny is already active!\033[0m' 1>&2;
                return
            fi;
            export CONNY_OLD_PATH="${PATH}"
            OPS1="$PS1"
            PS1="(\033[33m\033[1mconny\033[0m) $PS1"
            source "$CONNY_ENV_LOCATION/${environment}-activate.sh"
            __conny_hashr
            ;;
        deactivate)
            if [[ -v CONNY_OLD_PATH ]]; then
                source "$CONNY_ENV_LOCATION/${environment}-deactivate.sh"
                export PATH="${CONNY_OLD_PATH}"
                unset CONNY_OLD_PATH
                if [[ -v OPS1 ]]; then
                    PS1="$OPS1"
                    unset OPS1
                fi
                __conny_hashr
            else
                echo -e '\033[31m\033[1mconny is already deactivated!\033[0m' 1>&2;
            fi
            ;;
        *) 
            echo -e '\033[31m\033[1munknown argument use: "conny activate|deactivate"\033[0m' 1>&2;
            
            ;;
    esac

}
