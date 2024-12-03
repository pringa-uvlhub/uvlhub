from app.modules.featuremodel.repositories import FMMetaDataRepository, FeatureModelRepository
from app.modules.hubfile.services import HubfileService
from core.services.BaseService import BaseService
from app.modules.featuremodel.models import FeatureModel, FMMetaData
from app.modules.hubfile.models import Hubfile
from app import create_app, db
from flask import (
    redirect,
    render_template,
    request,
    jsonify,
    send_from_directory,
    make_response,
    abort,
    url_for,
)

class FeatureModelService(BaseService):
    def __init__(self):
        super().__init__(FeatureModelRepository())
        self.feature_model_repository = FeatureModelRepository
        self.fm_meta_data_repository = FMMetaDataRepository
        self.hubfile_service = HubfileService()

    def total_feature_model_views(self) -> int:
        return self.hubfile_service.total_hubfile_views()

    def total_feature_model_downloads(self) -> int:
        return self.hubfile_service.total_hubfile_downloads()

    def count_feature_models(self):
        return self.repository.count_feature_models()

    def copy_feature_model(self,original_feature_model,dataset_id):
        

        # Copiar el FMMetaData (si es necesario)
        new_fm_meta_data = self.fmmetadata_repository.create(
            uvl_filename=original_feature_model.fm_meta_data.uvl_filename,
            title=original_feature_model.fm_meta_data.title,
            description=original_feature_model.fm_meta_data.description,
            publication_type=original_feature_model.fm_meta_data.publication_type,
            publication_doi=original_feature_model.fm_meta_data.publication_doi,
            tags=original_feature_model.fm_meta_data.tags,
            uvl_version=original_feature_model.fm_meta_data.uvl_version,
            fm_metrics_id=original_feature_model.fm_meta_data.fm_metrics_id
        )
        # Crear una copia del FeatureModel
        new_feature_model = self.feature_model_repository.create(
            data_set_id=dataset_id,  
            fm_meta_data_id=new_fm_meta_data.id,
        )
        db.session.add(new_fm_meta_data)

        # Copiar los Hubfiles asociados al FeatureModel
        for original_file in original_feature_model.files:
            new_file = Hubfile(
                name=original_file.name,
                checksum=original_file.checksum,
                size=original_file.size,
                feature_model_id=new_feature_model.id,  # Asociamos el nuevo archivo con el nuevo FeatureModel
            )
            db.session.add(new_file)
        
        # Agregar el nuevo FeatureModel a la base de datos
        db.session.add(new_feature_model)
        db.session.commit()

        return jsonify({"message": "FeatureModel copiado exitosamente", "new_feature_model_id": new_feature_model.id}), 201

    class FMMetaDataService(BaseService):
        def __init__(self):
            super().__init__(FMMetaDataRepository())
