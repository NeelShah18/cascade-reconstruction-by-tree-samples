from collections import Counter
from itertools import chain

from sample_pool import TreeSamplePool
from tree_stat import TreeBasedStatistics
from random_steiner_tree.util import from_gt
from inference import infection_probability
from graph_tool.centrality import pagerank


def infection_probability_shortcut(g, edge_weights,
                                   obs,
                                   n_samples=5000,
                                   root_sampler=None,
                                   log=False,
                                   sampling_method='loop_erased'):

    gi = from_gt(g, edge_weights)
    # print('n_samples', n_samples)
    sampler = TreeSamplePool(g, n_samples, sampling_method, gi)
    sampler.fill(obs, root_sampler=root_sampler, log=log)
    est = TreeBasedStatistics(g)

    return infection_probability(g, obs, sampler=sampler, error_estimator=est)


def infer_edge_frequency(g, edge_weights, obs,
                         n_samples=5000,
                         sampling_method='loop_erased',
                         root_sampler=None,
                         log=False):
    gi = from_gt(g, edge_weights)
    # print('n_samples', n_samples)
    sampler = TreeSamplePool(g, n_samples, sampling_method, gi, return_type='tuples')
    sampler.fill(obs, root_sampler=root_sampler, log=log)
    samples_normalized = [[tuple(sorted(e)) for e in t]
                          for t in sampler.samples]
    return Counter(chain(*samples_normalized))


def pagerank_scores(g, obs, weight=None, eps=0.0):
    pers = g.new_vertex_property('float')
    pers.a += eps  # add some noise

    for o in obs:
        pers.a[o] = 1

    pers.a /= pers.a.sum()
    rank = pagerank(g, pers=pers, weight=weight)

    if rank.a.sum() == 0:
        raise ValueError('PageRank score all zero')

    p = rank.a / rank.a.sum()
    return p
