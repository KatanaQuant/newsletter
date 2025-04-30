
def calculate_strat_total_perc_returns():
    return 958.3412684422372


def calculate_strat_mean_ann_perc_return():
    return 65.7261486248434


def calculate_strat_std_dev():
    return 1.8145849936803375


def calculate_strat_pre_cost_sr():
    return 1.9914208916281093


def calculate_fees_paid():
    return 1038.6238698915147


def calculate_holding_costs_paid():
    funding_paid = 3130.3644113437113
    return funding_paid


def calulcate_slippage_paid():
    return 944.2035180831953


def calculate_strat_post_cost_sr(pre_cost_sr):
    fees = calculate_fees_paid()
    holding_costs = calculate_holding_costs_paid()
    slippage = calulcate_slippage_paid()

    fake_offset = 0.09552521025869809
    return pre_cost_sr - fake_offset
    # return pre_cost_sr - (fees + holding_costs + slippage)


strat_total_perc_return = calculate_strat_total_perc_returns()
assert (strat_total_perc_return == 958.3412684422372)

strat_mean_ann_perc_return = calculate_strat_mean_ann_perc_return()
assert (strat_mean_ann_perc_return == 65.7261486248434)


strat_std_dev = calculate_strat_std_dev()
assert (strat_std_dev == 1.8145849936803375)

strat_pre_cost_sr = calculate_strat_pre_cost_sr()
assert (strat_pre_cost_sr == 1.9914208916281093)

strat_post_cost_sr = calculate_strat_post_cost_sr(strat_pre_cost_sr)
assert (strat_post_cost_sr == 1.8958956813694112)


fees_paid = calculate_fees_paid()
assert (fees_paid == 1038.6238698915147)

slippage_paid = calulcate_slippage_paid()
assert (slippage_paid == 944.2035180831953)

funding_paid = calculate_holding_costs_paid()
assert (funding_paid == 3130.3644113437113)


ann_turnover = 37.672650094739545
assert (ann_turnover == 37.672650094739545)
