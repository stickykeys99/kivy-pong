from kivy.config import Config

Config.set('graphics','resizable',False)

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, StringProperty
from kivy.vector import Vector
from kivy.clock import Clock
from random import random, randrange
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.metrics import sp


class PongPaddle(Widget):

    score = NumericProperty(0)

    def bounce_ball(self, ball, p_no: int):
        if self.collide_widget(ball):
            speedup  = 1.3

            stuff = [abs(self.y - ball.top),abs(self.x-ball.right),abs(self.top-ball.y),abs(self.right-ball.x)]

            q = stuff.index(min(stuff))

            if q % 2:
                ball.velocity_x = -ball.velocity_x
            else:
                ball.velocity_y = -ball.velocity_y

            ball.velocity_x *= speedup
            ball.velocity_y *= speedup


class PongGame(Screen):
    name = StringProperty('game')

    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.winner = StringProperty('Player 0')

    def on_enter(self):
        self.serve_ball()

    def serve_ball(self):
        self.ball.center = self.center
        self.ball.velocity = (0,0)

        def _serve_ball(dt):
            self.ball.velocity = Vector(random()*randrange(-1,2,2),0.3*random()*randrange(-1,2,2)).normalize() * sp(4)

        Clock.schedule_once(_serve_ball,1.25)

    def serve_ball_caller(self,dt):
        self.serve_ball()

    def on_touch_move(self,touch):
        if touch.x < self.width/3:
            self.player1.center_y = touch.y
        if touch.x > self.width - self.width/3:
            self.player2.center_y = touch.y

    def update(self, dt):
        self.ball.move()

        self.player1.bounce_ball(self.ball,1)
        self.player2.bounce_ball(self.ball,2)

        # bounce ball off bottom or top
        if (self.ball.y < self.y) or (self.ball.top > self.top):
            self.ball.velocity_y *= -1

            speedup = 1.1
            self.ball.velocity_x *= speedup
            self.ball.velocity_y *= speedup

        # went of to a side to score point?
        if self.ball.x < self.x - sp(30):
            self.player2.score += 1
            self.serve_ball()
            if self.player2.score >= 11:
                self.player1.score = 0
                self.player2.score = 0
                App.get_running_app().root.set_winner('Player 2')
                App.get_running_app().root.current = 'restart'
            # Clock.schedule_once(self.serve_ball_caller,1)
        if self.ball.right > self.width + sp(30):
            self.player1.score += 1
            self.serve_ball()
            if self.player1.score >= 11:
                self.player1.score = 0
                self.player2.score = 0
                App.get_running_app().root.set_winner('Player 1')
                App.get_running_app().root.current = 'restart'
            # Clock.schedule_once(self.serve_ball_caller,1)


class PongMenu(Screen):
    name = StringProperty('menu')

    def update(self, dt):
        pass


class PongRestart(Screen):
    name = StringProperty('restart')

    def update(self, dt):
        pass


class PongManager(ScreenManager):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.transition = NoTransition()

    def update(self, dt):
        self.current_screen.update(dt)
    
    def set_winner(self, winner: str):
        self.pong_restart.restart_label.text = winner + ' wins!'


class PongApp(App):
    def build(self):
        sm = PongManager()

        Clock.schedule_interval(sm.update, 1.0/60.0)
        return sm


class PongBall(Widget):
    # velocity of the ball on x and y axis
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)

    # referencelist property so we can use ball.velocity as
    # a shorthand, just like e.g. w.pos for w.x and w.y
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    # ``move`` function will move the ball one step. This
    #  will be called in equal intervals to animate the ball
    def move(self):
        self.pos = Vector(*self.velocity) + self.pos


if __name__ == '__main__':
    PongApp().run()