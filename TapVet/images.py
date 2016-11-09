from PIL import Image as Img
from StringIO import StringIO
from django.core.files.uploadedfile import InMemoryUploadedFile


class ImageSerializerMixer(object):
    def image_with_background(self, img, size, output):
        '''
            Recieve the img and paste it on a white new image
            allowing to make a square image. offset variable, allowing
            to center the image.
        '''
        background = Img.new('RGB', size, 'white')
        offset = (size[0] - img.size[0]) / 2, (size[1] - img.size[1]) / 2
        background.paste(img, offset)
        background.save(output, format='JPEG', quality=70)
        output.seek(0)
        return output

    def image_no_background(self, img, size, output):
        '''
            Only save the image and change the output steam
        '''
        img.save(output, format='JPEG', quality=70)
        output.seek(0)
        return output

    def image_resize(self, size, img, image_stream):
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img.thumbnail(size, Img.ANTIALIAS)
        '''
        Two choices:

        output = self.image_no_background(img, size, StringIO())

        Will return an image with no white background, this means that the
        image will no be a square image.

        output = self.image_with_background(img, size, StringIO())

        Will return  an image with a white background, making this a square
        image.

        This choices will be helpful in  near the future when the client see
        the feed frontend and choose one or the other.

        '''
        output = self.image_with_background(img, size, StringIO())
        image = InMemoryUploadedFile(
            output, 'ImageField', "%s.jpg" % image_stream.name.split('.')[0],
            'image/jpeg', output.len, None)
        return image
