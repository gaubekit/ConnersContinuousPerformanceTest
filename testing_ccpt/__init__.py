from otree.api import *
import random, statistics, json

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'testing_ccpt'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    # --- Parameter (anpassen nach Bedarf) ---
    N_TRIALS = 30  # Demo: 30 Trials (echte Version ~360)
    NO_GO_LETTER = 'X'
    NO_GO_RATE = 0.10
    LETTERS = [chr(i) for i in range(65, 91)]
    STIM_DURATION_MS = 400 # original 250
    ISI_RANGE_MS = (1500, 2500)
    RESPONSE_KEY = ' '


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    results_json = models.LongStringField()
    hits = models.IntegerField()
    omissions = models.IntegerField()
    commissions = models.IntegerField()
    mean_rt_ms = models.IntegerField()
    sd_rt_ms = models.IntegerField()


# HELPFUNCTIONS
def make_trial_sequence():
    n_no_go = int(C.N_TRIALS * C.NO_GO_RATE)
    n_go = C.N_TRIALS - n_no_go
    go_letters = [l for l in C.LETTERS if l != C.NO_GO_LETTER]

    trials = []
    trials += [{'letter': C.NO_GO_LETTER, 'is_no_go': True} for _ in range(n_no_go)]
    trials += [{'letter': random.choice(go_letters), 'is_no_go': False} for _ in range(n_go)]
    random.shuffle(trials)

    for t in trials:
        t['isi_ms'] = random.randint(*C.ISI_RANGE_MS)
    return trials


def compute_summary_from_results(player: Player):
    data = json.loads(player.results_json)

    hits, omissions, commissions = 0, 0, 0
    rts = []

    for tr in data:
        is_no_go = tr['is_no_go']
        responded = tr['responded']
        rt = tr.get('rt_ms', None)

        if not is_no_go:
            if responded:
                hits += 1
                if rt is not None:
                    rts.append(rt)
            else:
                omissions += 1
        else:
            if responded:
                commissions += 1

    player.hits = hits
    player.omissions = omissions
    player.commissions = commissions
    player.mean_rt_ms = int(statistics.mean(rts)) if rts else 0
    player.sd_rt_ms = int(statistics.pstdev(rts)) if len(rts) > 1 else 0


# PAGES
class Intro(Page):
    pass


class AssessmentTaskCCPT(Page):
    form_model = 'player'
    form_fields = ['results_json']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            RESPONSE_KEY=C.RESPONSE_KEY,
            STIM_DURATION_MS=C.STIM_DURATION_MS,
            TRIALS=make_trial_sequence(),
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        compute_summary_from_results(player)


class Results(Page):
    pass


page_sequence = [Intro, AssessmentTaskCCPT, Results]
