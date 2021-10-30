# These should work with both bash and zsh
#
# To use these, put 'source /path/to/this/repo/functions.sh'
# in your shell profile
#
# these use a bunch of common-ish shell tools
# to interact with the hpi query JSON API
# jq: https://github.com/stedolan/jq
# fzf: https://github.com/junegunn/fzf

alias hq='hpi query'

# helpers used across multiple functions
alias mpv-from-stdin='mpv --playlist=- --no-audio-display --msg-level=file=error'
filter_unique() {
	awk '!seen[$0]++'
}

#############
# my.albums
#############

alias albums-history='hpi query my.albums.history'
alias albums-to-listen='hpi query my.albums.to_listen'
# how many albums I have on my list that I havent listened to yet
alias albums-left='albums-to-listen | jq length'
# pipe a list of album blobs to this to describe them
albums-describe() {
	jq -r '"\(.cover_artists) - \(.album_name) (\(.year))"'
}
albums-describe-score() {
	jq -r '"[\(.score) | \(.listened_on)] \(.cover_artists) - \(.album_name) (\(.year))"'
}
# any albums which I can't find/have to order physical copies for to listen to
alias albums-cant-find="hpi query -s my.albums._albums_cached | jq -r 'select(.note==\"cant find\")' | albums-describe"
# list any albums I have yet to listen to, sorted by how many awards they've won
albums-awards() {
	local COUNT="${1:-10}"
	albums-to-listen | jq -r "sort_by(.reasons | length) | reverse | .[0:${COUNT}] | .[] | \"[\(.reasons | length)] \(.album_name) - \(.cover_artists) (\(.year))\""
}
# just the next albums I should listen to chronologically
albums-next() {
	hpi query my.albums.to_listen -s --limit "${1:-10}" | albums-describe
}
alias albums-next-all='albums-next 99999'
alias albums-history-desc='albums-history -s | albums-describe-score'
# albums-history -s | albums-filter-reason 'Grammy for Best Rock' | albums-describe-score
# hq my.albums.to_listen -s | albums-filter-reason 'Contemporary Blues' | albums-describe
albums-filter-reason() {
	local reason
	reason="${1:?provide reason to filter by as first argument}"
	jq "select(.reasons | .[] | contains(\"${reason}\"))"
}
albums-filter-genre() {
	local genre
	genre="${1:?provide genre or style to filter by as first argument}"
	# lower what the user gave, as well as the genres/styles so can compare
	genre="$(echo "${genre}" | tr '[:upper:]' '[:lower:]')"
	jq "select((.genres + .styles) | .[] |= ascii_downcase | .[] | contains(\"${genre}\"))"
}

###################
# my.listenbrainz
###################

scrobbles() {
	hpi query my.listenbrainz.history -s "$@"
}
scrobble-describe() {
	jq -r '"\(.listened_at) \(.artist_name) - \(.track_name)"'
}

##########
# my.mpv
##########

# functions to replay music I've listened to recently
mpv-recent() {
	hpi query my.mpv.history --order-type datetime --reverse -s --limit "${1:-1}"
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
	hpi query 'my.trakt.history' -s "$@" | trakt-filter-movies
}

# e.g. trakt-episodes --recent 4w | trakt-describe-episode
trakt-episodes() {
	hpi query 'my.trakt.history' -s "$@" | trakt-filter-episodes
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
