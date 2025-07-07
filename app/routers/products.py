from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas
from ..db import get_db

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/categories", response_model=schemas.Category)
def create_category(category: schemas.Category, db: Session = Depends(get_db)):
    db_cat = models.Category(name=category.name)
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat


@router.get("/categories", response_model=List[schemas.Category])
def list_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).all()

@router.get("/", response_model=List[schemas.Product])
def list_products(q: Optional[str] = Query(None), category_id: Optional[int] = None, sort_by: str = Query("name"), db: Session = Depends(get_db)):
    query = db.query(models.Product)
    if q:
        query = query.filter(models.Product.name.ilike(f"%{q}%"))
    if category_id:
        query = query.filter(models.Product.category_id == category_id)
    if sort_by == "price":
        query = query.order_by(models.Product.price)
    else:
        query = query.order_by(models.Product.name)
    return query.all()

@router.post("/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.put("/{product_id}", response_model=schemas.Product)
def update_product(product_id: int, product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in product.dict().items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
    return {"detail": "deleted"}


@router.post("/{product_id}/reviews", response_model=schemas.Review)
def add_review(product_id: int, review: schemas.Review, db: Session = Depends(get_db)):
    if not db.query(models.Product).filter(models.Product.id == product_id).first():
        raise HTTPException(status_code=404, detail="Product not found")
    db_review = models.Review(**review.dict())
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review


@router.get("/{product_id}/reviews", response_model=List[schemas.Review])
def list_reviews(product_id: int, db: Session = Depends(get_db)):
    return db.query(models.Review).filter(models.Review.product_id == product_id).all()
