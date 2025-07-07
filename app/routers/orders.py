from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..db import get_db

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/", response_model=schemas.Order)
def create_order(order_items: List[schemas.OrderItem], user_id: int, promo_code: str | None = None, db: Session = Depends(get_db)):
    order = models.Order(user_id=user_id, status=models.OrderStatusEnum.PLACED)
    db.add(order)
    total = 0
    for item in order_items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if not product or product.stock < item.quantity:
            raise HTTPException(status_code=400, detail="Invalid product or not enough stock")
        product.stock -= item.quantity
        oi = models.OrderItem(order=order, product_id=item.product_id, quantity=item.quantity, price=product.price)
        db.add(oi)
        total += product.price * item.quantity
    if promo_code:
        promo = db.query(models.PromoCode).filter(models.PromoCode.code == promo_code, models.PromoCode.active == True).first()
        if promo:
            total = total * (100 - promo.discount_percent) / 100
    order.total = total
    db.commit()
    db.refresh(order)
    return order

@router.get("/{order_id}", response_model=schemas.Order)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.put("/{order_id}/status")
def update_status(order_id: int, status: models.OrderStatusEnum, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = status
    db.commit()
    return {"detail": "status updated"}

@router.post("/{order_id}/cancel")
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = models.OrderStatusEnum.CANCELLED
    db.commit()
    return {"detail": "order cancelled"}


@router.post("/{order_id}/return")
def return_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = models.OrderStatusEnum.CANCELLED
    db.commit()
    return {"detail": "order returned"}


@router.get("/{order_id}/tracking")
def track_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"status": order.status, "tracking_number": order.tracking_number}


@router.post("/{order_id}/slot")
def assign_slot(order_id: int, slot_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    slot = db.query(models.DeliverySlot).filter(models.DeliverySlot.id == slot_id, models.DeliverySlot.available == True).first()
    if not order or not slot:
        raise HTTPException(status_code=404, detail="Order or slot not found")
    slot.available = False
    order.delivery_slot = slot
    db.commit()
    return {"detail": "slot assigned"}
