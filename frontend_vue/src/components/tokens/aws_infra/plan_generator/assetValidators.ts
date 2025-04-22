import * as yup from 'yup';

export const S3Bucket_schema = yup.object().shape({
  bucket_name: yup.string().required().label('Bucket Name'),
  objects: yup.array().of(
    yup.object().shape({
      object_path: yup.string().required().label('Object Path'),
    })
  ),
});

export const Default_schema = yup.object();
