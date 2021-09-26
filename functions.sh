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

#############
# my.albums
#############

# how many albums I have on my list that I havent listened to yet
alias albums-left='hpi query my.albums.to_listen | jq length'
# pipe a list of album blobs to this to describe them
albums-describe() {
	jq -r '"\(.album_name) - \(.cover_artists) (\(.year))"'
}
albums-describe-score() {
	jq -r '"[\(.score) | \(.listened_on)] \(.album_name) - \(.cover_artists) (\(.year))"'
}
# any albums which I can't find/have to order physical copies for to listen to
alias albums-cant-find="hpi query -s my.albums._albums_cached | jq -r 'select(.note==\"cant find\")' | albums-describe"
# list any albums I have yet to listen to, sorted by how many awards they've won
albums-awards() {
	local COUNT="${1:-10}"
	hpi query my.albums.to_listen | jq -r "sort_by(.reasons | length) | reverse | .[0:${COUNT}] | .[] | \"[\(.reasons | length)] \(.album_name) - \(.cover_artists) (\(.year))\""
}
# just the next albums I should listen to chronologically
albums-next() {
	hpi query my.albums.to_listen -s --limit "${1:-10}" | jq -r '"\(.year) | \(.album_name) - \(.cover_artists)"'
}

##########
# my.mpv
##########

# functions to replay music I've listened to recently
mpv-recent() {
	hpi query my.mpv.history --order-type datetime --reverse -s --limit "${1:-1}"
}
mpv-recent-paths() {
	mpv-recent "$1" | jq -r .path
}
alias replay='mpv-recent-paths | mpv-from-stdin'
replay-recent() {
	mpv-recent-paths "${1:-$LINES}" | fzf | mpv-from-stdin
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
	hpi query my.trakt.ratings -s "$@" | trakt-filter-movies
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
	jq -r '"\(.media_data.title) (\(.media_data.year)) \(.rating)/10"'
}

trakt-describe-episode() {
	jq -r '"\(.media_data.show.title) (\(.media_data.show.year)) - S\(.media_data.season)E\(.media_data.episode) \(.media_data.title)"'
}
