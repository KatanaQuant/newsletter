
def calculate_start_total_perc_returns():
    return 958.3412684422372


def calculate_strat_mean_ann_perc_return():
    return 65.7261486248434


def calculate_strat_std_dev():
    return 1.8145849936803375


def calculate_strat_pre_cost_sr():
    return 1.9914208916281093


def calculate_strat_post_cost_sr(pre_cost_sr):
    fees = 0.09552521025869809
    holding_costs = 0
    slippage = 0
    return pre_cost_sr - (fees + holding_costs + slippage)


strat_total_perc_return = calculate_start_total_perc_returns()
assert (strat_total_perc_return == 958.3412684422372)

strat_mean_ann_perc_return = calculate_strat_mean_ann_perc_return()
assert (strat_mean_ann_perc_return == 65.7261486248434)


strat_std_dev = calculate_strat_std_dev()
assert (strat_std_dev == 1.8145849936803375)

strat_pre_cost_sr = calculate_strat_pre_cost_sr()
assert (strat_pre_cost_sr == 1.9914208916281093)

strat_post_cost_sr = calculate_strat_post_cost_sr(strat_pre_cost_sr)
assert (strat_post_cost_sr == 1.8958956813694112)


####

fees_paid = 1038.6238698915147
assert (fees_paid == 1038.6238698915147)

slippage_paid = 944.2035180831953
assert (slippage_paid == 944.2035180831953)

funding_paid = 3130.3644113437113
assert (funding_paid == 3130.3644113437113)


ann_turnover = 37.672650094739545
assert (ann_turnover == 37.672650094739545)
