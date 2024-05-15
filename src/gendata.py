import numpy as np

_identities = np.stack((np.identity(3), np.identity(3)[::-1]), axis=0)


def to_state(seq_state, player_id):

  player_1 = seq_state % 2
  player_2 = (seq_state + 1) * (seq_state > 0) % 2
  state = (player_2 - player_1) * (2 * player_id - 1)

  return state


def gen_sums(state):

  h_sums = state.sum(axis=-1)
  v_sums = state.sum(axis=-2)
  c_sums = np.tensordot(state, _identities, axes=[[-2, -1], [-2, -1]])

  return h_sums, v_sums, c_sums


def gen_clos(sums, amt):

  h_sums, v_sums, c_sums = sums

  h_clos = h_sums == amt
  v_clos = v_sums == amt
  c_clos = c_sums == amt

  return h_clos, v_clos, c_clos


def gen_mask(clos):

  h_clos, v_clos, c_clos = clos

  g_mask = h_clos.reshape(h_clos.shape + (1,)) + v_clos.reshape(v_clos.shape[:-1] + (1, 3))
  c_mask = np.tensordot(c_clos, _identities, axes=[-1, 0])
  p_mask = g_mask + c_mask > 0

  return p_mask


def gen_movs(m_mask, w_mask, state):

  empty = state == 0
  m_movs = empty * m_mask
  w_movs = empty * w_mask
  
  free = (m_movs + w_movs).any(axis=(-2, -1)) == 0
  m_movs = m_movs + empty * free.reshape(free.shape + (1, 1))

  return m_movs, w_movs


def gen_seq(movs, seq_state, stp):

  a_inds = np.where(movs)
  s_inds = a_inds[0]
  pm_inds = a_inds[1:]
  m_inds = np.arange(s_inds.shape[0]), *pm_inds

  new_seq_state = seq_state[s_inds]
  new_seq_state[*m_inds] = stp + 1

  return new_seq_state


def step(seq_state, stp):

  player_id = stp % 2
  state = to_state(seq_state, player_id)
  sums = gen_sums(state)

  m_clos = gen_clos(sums, -2)
  w_clos = gen_clos(sums, 2)

  m_mask = gen_mask(m_clos)
  w_mask = gen_mask(w_clos)

  m_movs, w_movs = gen_movs(m_mask, w_mask, state)

  new_seq_state = gen_seq(m_movs, seq_state, stp)
  won_seq_state = gen_seq(w_movs, seq_state, stp)

  return new_seq_state, won_seq_state


def solve(moves=9):

  ss = seq_state = np.zeros((1, 3, 3), np.int8)
  done_seq_state = [np.zeros((0, 3, 3), np.int8) for i in range(2)]

  for stp in range(moves):
    seq_state, won_seq_state = step(seq_state, stp)
    player_id = stp % 2
    done_seq_state[player_id] = np.concatenate((done_seq_state[player_id], won_seq_state), axis=0)

  return *done_seq_state, seq_state


def translate(seq_state, moves):

  seq_state = seq_state.reshape(-1, 9)
  length = seq_state.shape[0]
  seq = np.zeros((length, moves), np.int8) - 1

  for move in range(moves):
    game, pos = np.where(seq_state == move + 1)
    seq[game, move] = pos

  return seq


if __name__ == '__main__':

  moves = 9

  x_seq_state, o_seq_state, d_seq_state = solve(moves)

  x_seq = translate(x_seq_state, moves)
  o_seq = translate(o_seq_state, moves)
  d_seq = translate(d_seq_state, moves)
