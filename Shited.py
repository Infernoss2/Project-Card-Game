from Cards import Deck
from Player import Player
from Game import Game

def main():
    game = Game()

    game.add_player("Sagi")
    game.add_player("Bot")

    game.deck.shuffle()
    game.deal_cards()

    for player in game.Players:
        game.choose_face_up_cards(player)

    for player in game.Players:
        print(f"\n{player.name} face-up cards:")
        for card in player.face_up:
            print(card)
        print(f"\n{player.name} hand cards:")
        for card in player.hand:
            print(card)







if __name__ == "__main__":
    main()
