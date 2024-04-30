import quarto
from geneticAlgorithm import GeneticPlayer
from main import RandomPlayer

def main():
    win = 0
    draw = 0
    loss = 0
    num_matches = 200
    first_player = False
    
    for i in range(num_matches):
        game = quarto.Quarto()
        
        #print("-------- MATCH ", i)
        if first_player:
            game.set_players((GeneticPlayer(game), RandomPlayer(game)))
        else:
            game.set_players((RandomPlayer(game), GeneticPlayer(game)))  
        
        winner = game.run()
        
        if first_player:
            if winner == 0:
                win = win + 1
            elif winner == -1:
                draw = draw + 1
            else:
                loss = loss + 1
        else:
            if winner == 1:
                win = win + 1
            elif winner == -1:
                draw = draw + 1
            else:
                loss = loss + 1
            
        
        #print("Winner is: ", winner)
        win_rate = win / (i+1)
        draw_rate = draw / (i+1)
        loss_rate = loss / (i+1)
        if winner == 1 or winner == 0:
            print(f"Match # {i+1} -> Winner = {type(game._Quarto__players[winner]).__name__} -> Win rate = {win_rate}, Draw rate = {draw_rate} Loss rate = {loss_rate}")
        else:
            print(f"Match # {i+1} -> Winner = Both -> Win rate = {win_rate}, Draw rate = {draw_rate} Loss rate = {loss_rate}")
        
    win_rate = win / num_matches
    print(f"Win rate = {win_rate}")

if __name__ == '__main__':
    main()