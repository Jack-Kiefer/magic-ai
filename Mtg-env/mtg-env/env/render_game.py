import tkinter as tk
from PIL import Image, ImageTk
import threading
import time
from mtg_env import mtg_env


class MTGRender:
    def __init__(self, env):
        self.env = env
        self.root = tk.Tk()
        self.root.title("Magic: The Gathering Game Environment")

        self.w = 800
        self.h = 800
        self.canvas = tk.Canvas(self.root, width=self.w, height=self.h)
        self.canvas.pack()
        self.cardw = 250//3
        self.cardh = 350//3
        self.margin = 10

        self.images = {}
        self.tapped_images = {}
        self.load_images()  # Load images in the main thread

        # Create a frame for action buttons
        self.action_frame = tk.Frame(self.root)
        self.action_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.action_buttons = []

    def load_image(self, path):
        image = Image.open(path)
        image = image.resize((self.cardw, self.cardh))
        return ImageTk.PhotoImage(image)

    def load_tapped_image(self, path):
        image = Image.open(path)
        image = image.rotate(270)
        image = image.resize((self.cardh, self.cardw))
        return ImageTk.PhotoImage(image)

    def load_images(self):
        for card in self.env.state.decks[0] + self.env.state.hands[0]:
            self.images[card.name] = self.load_image(card.image_path)
            self.tapped_images[card.name] = self.load_tapped_image(card.image_path)

    def calculateStart(self, num_cards):
        return 100 + (self.w-100 - num_cards*(self.cardw + self.margin)) / 2

    def draw_player_area(self, player, hand_y, lands_y, creatures_y):
        self.canvas.create_text(50, hand_y+self.cardh/2, text=str(self.env.state.life[player]), fill="black", font=('Helvetica 30 bold'))

        start = self.calculateStart(len(self.env.state.hands[player]))
        for card in self.env.state.hands[player]:
            image = self.images[card.name]
            self.canvas.create_image(start, hand_y, image=image, anchor='nw')
            start += self.cardw + self.margin

        untappedLands = self.env.state.untappedLands[player]
        tappedLands = self.env.state.totalLands[player] - self.env.state.untappedLands[player]
        start = self.calculateStart(untappedLands + tappedLands)
        for card in range(untappedLands):
            image = self.images["Forest"]
            self.canvas.create_image(start, lands_y, image=image, anchor='nw')
            start += self.cardw + self.margin
        for card in range(tappedLands):
            image = self.tapped_images["Forest"]
            self.canvas.create_image(start, lands_y, image=image, anchor='nw')
            start += self.cardw + self.margin

        start = self.calculateStart(len(self.env.state.creatures[player]))
        for card in self.env.state.creatures[player]:
            if card.tapped:
                image = self.tapped_images[card.name]
            else:
                image = self.images[card.name]
            self.canvas.create_image(start, creatures_y, image=image, anchor='nw')
            start += self.cardw + self.margin

    def draw_board(self):
        self.canvas.delete("all")
        if self.env.state.turn == 0:
            self.canvas.create_rectangle(0, 0, self.w, self.h/2, fill="#FDF3B1")
        else:
            self.canvas.create_rectangle(0, self.h / 2, self.w, self.h, fill="#FDF3B1")
        self.draw_player_area(0, 25, 150, 275)
        self.draw_player_area(1, 650, 525, 400)

    def update(self):
        self.draw_board()

    def doAction(self, action):
        self.env.step(action)
        self.update()
        while sum(self.env.infos[self.env.agent_selection]['action_mask']) == 1:
            self.env.step(0)
            self.update()
        self.update_actions()

    def getActionDesc(self, action):
        name, data = self.env.mask_to_action(action)
        if name == "pass_priority":
            return "Pass Priority"
        if name == "play_card":
            return f"Play {self.env.distinct_cards[data].name}"
        if name == "attack":
            return f"Attack with {self.env.distinct_creatures[data].name}"
        if name == "block":
            return f"Block {self.env.distinct_creatures[data[0]].name} with {self.env.distinct_creatures[data[1]].name}"

    def update_actions(self):
        for button in self.action_buttons:
            button.destroy()
        self.action_buttons.clear()

        agent = self.env.agent_selection
        action_mask = self.env.infos[agent]['action_mask']
        for i, available in enumerate(action_mask):
            if available:
                button = tk.Button(self.action_frame, text=f"{self.getActionDesc(i)}",
                                   command=lambda i=i: self.doAction(i))
                button.pack(side=tk.LEFT)
                self.action_buttons.append(button)

    def run(self):
        self.update()
        self.update_actions()
        self.root.mainloop()

if __name__ == "__main__":
    env = mtg_env()
    renderer = MTGRender(env)
    renderer.run()
