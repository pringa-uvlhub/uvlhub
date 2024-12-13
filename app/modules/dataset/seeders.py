import os
import shutil
from app.modules.auth.models import User
from app.modules.featuremodel.models import FMMetaData, FeatureModel
from app.modules.hubfile.models import Hubfile
from core.seeders.BaseSeeder import BaseSeeder
from app.modules.dataset.models import (
    DataSet,
    DSMetaData,
    PublicationType,
    DSMetrics,
    Author)
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv


class DataSetSeeder(BaseSeeder):

    priority = 2  # Lower priority

    def run(self):
        # Retrieve users
        user1 = User.query.filter_by(email='user1@example.com').first()
        user2 = User.query.filter_by(email='user2@example.com').first()

        if not user1 or not user2:
            raise Exception("Users not found. Please seed users first.")

        # Create DSMetrics instance
        ds_metrics = [
            DSMetrics(number_of_models='5', number_of_features='50'),
            DSMetrics(number_of_models='7', number_of_features='40')]

        seeded_ds_metrics = self.seed(ds_metrics)

        # Create DSMetaData instances
        ds_meta_data_list = [
            DSMetaData(
                deposition_id=1 + i,
                title=f'Sample dataset {i+1}',
                description=f'Description for dataset {i+1}',
                publication_type=PublicationType.BOOK if i == 1 else PublicationType.DATA_MANAGEMENT_PLAN,
                publication_doi=f'10.1234/dataset{i+1}',
                build=False,
                dataset_doi=f'10.1234/dataset{i+1}',
                tags='tag1, tag2' if i == 2 else 'tag3',
                staging_area=False,
                ds_metrics_id=seeded_ds_metrics[0].id if i == 1 else seeded_ds_metrics[1].id
            ) for i in range(4)
        ]
        # Add an additional DSMetaData for the staging area
        ds_meta_data_list.append(
            DSMetaData(
                deposition_id=None,
                title='Staging area dataset',
                description='Description for staging area dataset',
                publication_type=PublicationType.NONE,
                publication_doi=None,
                build=False,
                dataset_doi=None,
                tags='tag1, tag2',
                staging_area=True,
                ds_metrics_id=seeded_ds_metrics.id
            )
        )
        seeded_ds_meta_data = self.seed(ds_meta_data_list)

        # Create Author instances and associate with DSMetaData
        authors = [
            Author(
                name=f'Author {i+1}',
                affiliation=f'Affiliation {i+1}',
                orcid=f'0000-0000-0000-000{i}',
                ds_meta_data_id=seeded_ds_meta_data[i % 4].id
            ) for i in range(4)
        ]
        self.seed(authors)

        # Create DataSet instances
        datasets = [
            DataSet(
                user_id=user1.id if i % 2 == 0 else user2.id,
                ds_meta_data_id=seeded_ds_meta_data[i].id,
                created_at=datetime.now(timezone.utc) - timedelta(days=i)
            ) for i in range(4)
        ]
        # Add an additional DataSet for the staging area
        staging_dataset = DataSet(
            user_id=user1.id,
            ds_meta_data_id=seeded_ds_meta_data[-1].id,  # The last DSMetaData is for the staging area
            created_at=datetime.now(timezone.utc)
        )
        datasets.append(staging_dataset)

        seeded_datasets = self.seed(datasets)

        # Assume there are 12 UVL files, create corresponding FMMetaData and FeatureModel
        fm_meta_data_list = [
            FMMetaData(
                uvl_filename=f'file{i+1}.uvl',
                title=f'Feature Model {i+1}',
                description=f'Description for feature model {i+1}',
                publication_type=PublicationType.SOFTWARE_DOCUMENTATION,
                publication_doi=f'10.1234/fm{i+1}',
                tags='tag1, tag2',
                uvl_version='1.0'
            ) for i in range(11)
        ]
        # Add an additional FMMetaData with publication_doi and tags set to None
        fm_meta_data_list.append(
            FMMetaData(
                uvl_filename='file12.uvl',
                title='Feature Model 12',
                description='Description for feature model 12',
                publication_type=PublicationType.NONE,
                publication_doi=None,
                tags=None,
                uvl_version='1.0'
            )
        )
        seeded_fm_meta_data = self.seed(fm_meta_data_list)

        # Create Author instances and associate with FMMetaData
        fm_authors = [
            Author(
                name=f'Author {i+5}',
                affiliation=f'Affiliation {i+5}',
                orcid=f'0000-0000-0000-000{i+5}',
                fm_meta_data_id=seeded_fm_meta_data[i].id
            ) for i in range(12)
        ]
        self.seed(fm_authors)

        feature_models = [
            FeatureModel(
                data_set_id=seeded_datasets[i // 3].id,
                fm_meta_data_id=seeded_fm_meta_data[i].id
            ) for i in range(11)
        ]
        # Add a FeatureModel for the staging dataset
        feature_models.append(
            FeatureModel(
                data_set_id=staging_dataset.id,
                fm_meta_data_id=seeded_fm_meta_data[-1].id  # The last FMMetaData is for the staging dataset
            )
        )
        seeded_feature_models = self.seed(feature_models)

        # Create files, associate them with FeatureModels and copy files
        load_dotenv()
        working_dir = os.getenv('WORKING_DIR', '')
        src_folder = os.path.join(working_dir, 'app', 'modules', 'dataset', 'uvl_examples')
        for i in range(12):
            file_name = f'file{i+1}.uvl'
            feature_model = seeded_feature_models[i]
            dataset = next(ds for ds in seeded_datasets if ds.id == feature_model.data_set_id)
            user_id = dataset.user_id

            dest_folder = os.path.join(working_dir, 'uploads', f'user_{user_id}', f'dataset_{dataset.id}')
            os.makedirs(dest_folder, exist_ok=True)
            shutil.copy(os.path.join(src_folder, file_name), dest_folder)

            file_path = os.path.join(dest_folder, file_name)

            uvl_file = Hubfile(
                name=file_name,
                checksum=f'checksum{i+1}',
                size=os.path.getsize(file_path),
                feature_model_id=feature_model.id
            )
            self.seed([uvl_file])
