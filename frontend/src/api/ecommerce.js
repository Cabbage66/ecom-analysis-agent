import request from '@/utils/request'

export function getProductPageList(params) {
  return request({
    url: '/api/ecommerce/products',
    method: 'get',
    params
  })
}

export function getOrderPageList(params) {
  return request({
    url: '/api/ecommerce/orders',
    method: 'get',
    params
  })
}

export function getReviewPageList(params) {
  return request({
    url: '/api/ecommerce/reviews',
    method: 'get',
    params
  })
}
