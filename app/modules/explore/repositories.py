import re
from sqlalchemy import or_
import unidecode
from app.modules.dataset.models import Author, DSMetaData, DataSet, PublicationType, DSMetrics
from app.modules.featuremodel.models import FMMetaData, FeatureModel
from core.repositories.BaseRepository import BaseRepository


class ExploreRepository(BaseRepository):
    def __init__(self):
        super().__init__(DataSet)

    def filter(
        self, query="", queryAuthor="", queryTag="", queryFeatures="", queryModels="", sorting="newest",
        publication_type="any", tags=[], **kwargs
    ):
        # Normalize and remove unwanted characters
        normalized_query = unidecode.unidecode(query).lower()
        cleaned_query = re.sub(r'[,.":\'()\[\]^;!¡¿?]', "", normalized_query)

        normalized_query_author = unidecode.unidecode(queryAuthor)
        cleaned_query_author = re.sub(r'[,.":\'()\[\]^;!¡¿?]', "", normalized_query_author)

        normalized_query_tag = unidecode.unidecode(queryTag)
        cleaned_query_tag = re.sub(r'[,.":\'()\[\]^;!¡¿?]', "", normalized_query_tag)

        normalized_query_features = unidecode.unidecode(queryFeatures)
        cleaned_query_features = re.sub(r'[,.":\'()\[\]^;!¡¿?]', "", normalized_query_features)

        normalized_query_models = unidecode.unidecode(queryModels)
        cleaned_query_models = re.sub(r'[,.":\'()\[\]^;!¡¿?]', "", normalized_query_models)

        filters = []
        filters.append(DSMetaData.title.ilike(f"%{cleaned_query}%"))
        filters.append(DSMetaData.description.ilike(f"%{cleaned_query}%"))
        filters.append(Author.name.ilike(f"%{cleaned_query}%"))
        filters.append(Author.affiliation.ilike(f"%{cleaned_query}%"))
        filters.append(Author.orcid.ilike(f"%{cleaned_query}%"))
        filters.append(FMMetaData.uvl_filename.ilike(f"%{cleaned_query}%"))
        filters.append(FMMetaData.title.ilike(f"%{cleaned_query}%"))
        filters.append(FMMetaData.description.ilike(f"%{cleaned_query}%"))
        filters.append(FMMetaData.publication_doi.ilike(f"%{cleaned_query}%"))
        filters.append(FMMetaData.tags.ilike(f"%{cleaned_query}%"))
        filters.append(DSMetaData.tags.ilike(f"%{cleaned_query}%"))

        filters_author = []
        filters_author.append(Author.name.contains(cleaned_query_author))
        filters_author.append(Author.affiliation.contains(cleaned_query_author))
        filters_author.append(Author.orcid.contains(cleaned_query_author))

        filters_tag = []
        filters_tag.append(FMMetaData.tags.contains(cleaned_query_tag))
        filters_tag.append(DSMetaData.tags.contains(cleaned_query_tag))

        filters_features = []
        filters_features.append(DSMetrics.number_of_features.contains(cleaned_query_features))

        filters_models = []
        filters_models.append(DSMetrics.number_of_models.contains(cleaned_query_models))

        datasets = (
            self.model.query
            .join(DataSet.ds_meta_data)
            .join(DSMetaData.authors)
            .join(DataSet.feature_models)
            .join(FeatureModel.fm_meta_data)
            .join(DSMetaData.ds_metrics)
            .filter(or_(*filters))
            .filter(or_(*filters_author))
            .filter(or_(*filters_tag))
            .filter(or_(*filters_features))
            .filter(or_(*filters_models))
            .filter(DSMetaData.dataset_doi.isnot(None))  # Exclude datasets with empty dataset_doi
        )

        if publication_type != "any":
            matching_type = None
            for member in PublicationType:
                if member.value.lower() == publication_type:
                    matching_type = member
                    break

            if matching_type is not None:
                datasets = datasets.filter(DSMetaData.publication_type == matching_type.name)

        # Order by created_at
        if sorting == "oldest":
            datasets = datasets.order_by(self.model.created_at.asc())
        else:
            datasets = datasets.order_by(self.model.created_at.desc())

        return datasets.all()
