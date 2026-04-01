1) Better logic for element -> link_terminal
2) Change 
        if callable(getattr(self._value_ref, "_value", None)):
            self._dynamic_label_timer = QtCore.QTimer(self)
            self._dynamic_label_timer.timeout.connect(self.refresh_value_label)
            self._dynamic_label_timer.start(250)
in element l100

Features
1) Operator node logic
2) RMS
3) AmplitudeTransformerNode with input_value and data ?
4) QtViz for graphes