import axios from 'axios';

export const getProduct = (pk) => {
  return axios.get(`/api/sketchbook/product/${pk}/`);
}
