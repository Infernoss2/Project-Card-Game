from Cards import Deck
from Player import Player
from Game import Game

def main():
    game = Game()

    game.add_player("Sagi")
    game.add_player("Bot")
    game.add_player("marcel")
    game.add_player("zorro")
    start_players_amount = len(game.Players)

    game.current_deck.shuffle()
    game.deal_cards()

    for player in game.Players:
        game.choose_face_up_cards(player)

    for player in game.Players:
        print(f"\n{player.name} face-up cards:")
        player.print_face_up()


        print(f"\n{player.name} hand cards:")
        for card in player.hand:
            print(card)

    while len(game.Players) > 1:

        for player in list(game.Players):
            if len(game.Players) <= 1:
                print("game over")
                break

            print(f"\nIt's {player.name}'s turn")
            player.print_face_up()
            print("\n")
            game.play_turn(player)




            if len(player.hand) == 0 and len(player.face_down) == 0:
                place = (start_players_amount + 1) - len(game.Players)
                print(f"\n{player.name} finished in place - {place}!")
                game.Players.remove(player)


if __name__ == "__main__":
    main()
