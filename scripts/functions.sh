#!/usr/bin/env bash
# These should work with both bash and zsh
#
# To use these, put 'source /path/to/this/repo/functions.sh'
# in your shell profile
#
# these use a bunch of common-ish shell tools
# to interact with the hpi query JSON API
# jq: https://github.com/stedolan/jq
# fzf: https://github.com/junegunn/fzf

# helpers used across multiple functions
alias mpv-from-stdin='mpv --playlist=- --no-audio-display --msg-level=file=error'
filter_unique() {
	awk '!seen[$0]++'
}

###################
# my.listenbrainz
###################

scrobbles() {
	hpi query my.listenbrainz.export.history -s "$@"
}
scrobble-describe() {
	jq -r '"\(.listened_at) \(.artist_name) - \(.track_name)"'
}

##########
# my.mpv
##########

# functions to replay music I've listened to recently
mpv-recent() {
	hpi query my.mpv.history_daemon.history --order-type datetime --reverse -s --limit "${1:-1}"
}
mpv-recent-path() {
	mpv-recent "$1" | jq -r .path
}
alias replay='mpv-recent-path | mpv-from-stdin'
replay-recent() {
	mpv-recent-path "${1:-$LINES}" | fzf | mpv-from-stdin
}

##########
# my.zsh
##########

# jq later to preserve newlines in commands
alias zsh-unique="hpi query -s my.zsh.history | jq '.command' | filter_unique | jq -r"
alias zsh-unique-fzf='zsh-unique | fzf'

############
# my.trakt
############

# e.g. trakt-movies --recent 4w | trakt-describe-movie
trakt-movies() {
	hpi query 'my.trakt.export.history' -s "$@" | trakt-filter-movies
}

# e.g. trakt-episodes --recent 4w | trakt-describe-episode
trakt-episodes() {
	hpi query 'my.trakt.export.history' -s "$@" | trakt-filter-episodes
}

trakt-filter-movies() {
	jq 'select(.media_type == "movie")'
}

trakt-filter-episodes() {
	jq 'select(.media_type == "episode")'
}

trakt-describe-movie() {
	jq -r '"\(.media_data.title) (\(.media_data.year))"'
}

trakt-describe-episode() {
	jq -r '"\(.media_data.show.title) (\(.media_data.show.year)) - S\(.media_data.season)E\(.media_data.episode) \(.media_data.title)"'
}
