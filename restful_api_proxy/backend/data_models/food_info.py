from __future__ import annotations
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class FoodNutrient(BaseModel):
    model_config = ConfigDict(extra="allow")

    nutrientId: int
    nutrientName: str
    nutrientNumber: str
    unitName: str
    value: float
    rank: int
    indentLevel: int
    foodNutrientId: int
    dataPoints: int | None = None
    derivationCode: str | None = None
    derivationDescription: str | None = None
    derivationId: int | None = None
    foodNutrientSourceId: int | None = None
    foodNutrientSourceCode: str | None = None
    foodNutrientSourceDescription: str | None = None
    min: float | None = None
    max: float | None = None
    percentDailyValue: float | int | None = None


class FoodCategory(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | None = None
    code: str | None = None
    description: str | None = None
    parentCategory: FoodCategory | None = None


class NutrientConversionFactors(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: str | None = None
    value: float | None = None
    proteinValue: float | None = None
    fatValue: float | None = None
    carbohydrateValue: float | None = None


class FoodAttribute(BaseModel):
    model_config = ConfigDict(extra="allow")

    value: str | None = None
    name: str | None = None
    id: int | None = None


class FoodAttributeType(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str | None = None
    description: str | None = None
    id: int | None = None
    foodAttributes: list[FoodAttribute] = Field(default_factory=list)


class FoodSearchCriteria(BaseModel):
    model_config = ConfigDict(extra="allow")

    dataType: list[str] | None = None
    query: str
    generalSearchInput: str
    pageNumber: int
    numberOfResultsPerPage: int
    pageSize: int
    requireAllWords: bool
    foodTypes: list[str] | None = None


class SRLegacyFoodItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    fdcId: int
    dataType: str
    description: str

    foodClass: str | None = None
    isHistoricalReference: bool | None = None
    ndbNumber: int | None = None
    publicationDate: str | None = None
    scientificName: str | None = None
    foodCategory: FoodCategory | str | None = None
    foodNutrients: list[FoodNutrient] = Field(default_factory=list)
    nutrientConversionFactors: list[NutrientConversionFactors] = Field(default_factory=list)

    publishedDate: str | None = None
    modifiedDate: str | None = None
    gtinUpc: str | None = None
    brandOwner: str | None = None
    brandName: str | None = None
    subbrandName: str | None = None
    ingredients: str | None = None
    marketCountry: str | None = None
    dataSource: str | None = None
    servingSizeUnit: str | None = None
    servingSize: float | None = None
    householdServingFullText: str | None = None
    packageWeight: str | None = None
    shortDescription: str | None = None
    allHighlightFields: str | None = None
    score: float | None = None
    commonNames: str | None = None
    additionalDescriptions: str | None = None
    microbes: list[Any] = Field(default_factory=list)
    finalFoodInputFoods: list[Any] = Field(default_factory=list)
    foodMeasures: list[Any] = Field(default_factory=list)
    foodAttributes: list[FoodAttribute] = Field(default_factory=list)
    foodAttributeTypes: list[FoodAttributeType] = Field(default_factory=list)
    foodVersionIds: list[Any] = Field(default_factory=list)
    tradeChannels: list[str] = Field(default_factory=list)

class FoodInfo(SRLegacyFoodItem):
    pass

class Aggregations(BaseModel):
    model_config = ConfigDict(extra="allow")

    dataType: dict[str, int]
    nutrients: dict[str, Any]


class FoodInfoResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    totalHits: int
    currentPage: int
    totalPages: int
    pageList: list[int]
    foodSearchCriteria: FoodSearchCriteria
    foods: list[FoodInfo]
    aggregations: Aggregations | None = None
