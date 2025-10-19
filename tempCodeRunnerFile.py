if self.sprite and act in ("UP", "DOWN", "LEFT", "RIGHT"):
                    self.sprite.direction = {"UP": "up", "DOWN": "down", "LEFT": "left", "RIGHT": "right"}[act]
                    #self.sprite.update()