import axios from 'axios';

export const getProduct = (pk) => {
  return axios.get(`/api/sketchbook/product/${pk}/`);
}

export const getProductKindConfiguration = (pk) => {
  return axios.get('/api/sketchbook/configurations/', {params: {product_kind_id: pk}})
}
