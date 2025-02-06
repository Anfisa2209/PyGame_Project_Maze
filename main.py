from main_page import main
from game_code import play_music
if __name__ == '__main__':
    song = play_music('music.mp3', True)
    INF = 9999
    song.play(INF)
    main(0)
