from vtkmodules.vtkIOXML import vtkXMLImageDataReader


def read_vti(data_filename: str):
    reader = vtkXMLImageDataReader()
    reader.SetFileName(data_filename)
    reader.Update()
    return reader
