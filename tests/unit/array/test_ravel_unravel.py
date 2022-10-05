import numpy as np
import pytest
import torch
from scipy.sparse import csr_matrix, coo_matrix, bsr_matrix, csc_matrix

from docarray import DocumentArray, Document
from docarray.math.ndarray import to_numpy_array


def get_ndarrays_for_ravel():
    a = np.random.random([10, 3])
    a[a > 0.5] = 0
    return [
        (a, False),
        (torch.tensor(a), False),
        (torch.tensor(a).to_sparse(), True),
        (csr_matrix(a), True),
        (bsr_matrix(a), True),
        (coo_matrix(a), True),
        (csc_matrix(a), True),
    ]


@pytest.mark.parametrize('ndarray_val, is_sparse', get_ndarrays_for_ravel())
@pytest.mark.parametrize('attr', ['embeddings', 'tensors'])
@pytest.mark.parametrize(
    'da_cls',
    [
        DocumentArray,
    ],
)
def test_ravel_embeddings_tensors(ndarray_val, attr, is_sparse, da_cls):
    da = da_cls.empty(10)
    setattr(da, attr, ndarray_val)
    ndav = getattr(da, attr)

    # test read/getter
    assert type(ndav) is type(ndarray_val)

    if is_sparse:
        if hasattr(ndav, 'todense'):
            ndav = (ndav.todense(),)
            ndarray_val = ndarray_val.todense()
        if hasattr(ndav, 'to_dense'):
            ndav = (ndav.to_dense(),)
            ndarray_val = ndarray_val.to_dense()

    if isinstance(ndav, tuple):
        ndav = ndav[0]
    if hasattr(ndav, 'numpy'):
        ndav = ndav.numpy()
        ndarray_val = ndarray_val.numpy()

    np.testing.assert_almost_equal(ndav, ndarray_val)


@pytest.mark.parametrize('sparse_cls', [csr_matrix, csc_matrix, bsr_matrix, coo_matrix])
def test_bsr_coo_unravel(sparse_cls):
    a = np.random.random([10, 72])
    a[a > 0.5] = 0

    da = DocumentArray.empty(10)
    for d, a_row in zip(da, a):
        d.embedding = sparse_cls(a_row)

    np.testing.assert_almost_equal(a, da.embeddings.todense())


def get_ndarrays():
    a = np.random.random([10, 3])
    a[a > 0.5] = 0
    return [
        (a, False),
        (torch.tensor(a), False),
        (torch.tensor(a).to_sparse(), True),
        (csr_matrix(a), True),
        (bsr_matrix(a), True),
        (coo_matrix(a), True),
        (csc_matrix(a), True),
    ]


@pytest.mark.parametrize('ndarray_val, is_sparse', get_ndarrays())
@pytest.mark.parametrize('attr', ['embedding', 'tensor'])
def test_ndarray_force_numpy(ndarray_val, attr, is_sparse):
    d = Document()
    setattr(d, attr, ndarray_val)
    ndav = to_numpy_array(getattr(d, attr))
    assert isinstance(ndav, np.ndarray)
    assert ndav.shape == (10, 3)
