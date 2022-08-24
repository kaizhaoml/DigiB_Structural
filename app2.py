import os
import io
import numpy as np
import pandas as pd
from vtk import (vtkUnstructuredGridReader, vtkDataSetMapper, vtkActor,vtkScalarBarActor,vtkScalarBarWidget,
                 vtkRenderer, vtkRenderWindow, vtkRenderWindowInteractor, vtkExtractVectorComponents,vtkVectorNorm)
from vtkmodules.vtkCommonCore import vtkPoints, vtkIdList,vtkLookupTable
from vtkmodules.vtkCommonDataModel import vtkUnstructuredGrid, vtkCellArray
from vtkmodules.vtkFiltersCore import vtkThreshold
from vtkmodules.numpy_interface.dataset_adapter import numpyTovtkDataArray as np2da
from vtkmodules.util import vtkConstants
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch
import glob
from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vuetify, vtk, html, trame
from trame.ui.vuetify import VAppLayout
from trame.app import get_server
from trame.ui.vuetify import SinglePageWithDrawerLayout
from trame.widgets import vtk, vuetify, trame
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch
from vtkmodules.vtkFiltersCore import vtkThreshold
from vtkmodules.vtkRenderingAnnotation import vtkCubeAxesActor
from trame.assets.local import LocalFileManager

import vtkmodules.vtkRenderingOpenGL2

dirName = os.path.dirname(__file__)

server = get_server()
ctrl = server.controller
state = server.state


def ui_card(title):
    with vuetify.VCard():
        vuetify.VCardTitle(
            title,
            classes="red darken-2 py-1 white--text text--darken-3",
            style="user-select: none; cursor: pointer",
            hide_details=True,
            dense=True,
        )
        content = vuetify.VCardText(classes="py-2")
    return content


from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor
)


renderer = vtkRenderer()
renderer_window = vtkRenderWindow()
renderer_window.AddRenderer(renderer)

renderWindowInteractor = vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderer_window)
renderWindowInteractor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

ListFiles = glob.glob(dirName + r"\1/*.vtk")


def GetModeScalar(mode_shapes):
    ScalerangeFile = dirName +"\\" + str(mode_shapes+1)+ "\MG_N.vtk"
    reader = vtkUnstructuredGridReader()
    reader.SetFileName(ScalerangeFile)
    reader.Update()
    output = reader.GetOutput()
    getScalars = vtkExtractVectorComponents()
    getScalars.SetInputData(output)
    getScalars.Update()
    output = getScalars.GetOutput()
    scalar_range = output.GetScalarRange()
    return scalar_range


scalar_range = GetModeScalar(0)
ListofActors = []
ListofReaders = []
ListofMappers = []

lut = vtkLookupTable()
lut.SetTableRange(scalar_range)
lut.SetNumberOfColors(10)
lut.Build()

def originalLayer():
    ListO = glob.glob(dirName + r"\Orig/*.vtk")
    OrigLayers = []
    for icount, file in enumerate(ListO):
        reader = vtkUnstructuredGridReader()
        reader.SetFileName(file)
        reader.Update()

        output = reader.GetOutput()
        output_port = reader.GetOutputPort()

        getScalars = vtkExtractVectorComponents()
        getScalars.SetInputData(output)
        getScalars.Update()

        getScalars.Update()
        output = getScalars.GetOutput()
        output_port = getScalars.GetOutputPort()

        mapper = vtkDataSetMapper()
        mapper.SetInputConnection(output_port)
        mapper.SetScalarVisibility(0)
        # mapper.SetLookupTable(lut)

        actor = vtkActor()
        actor.SetMapper(mapper)
        property = actor.GetProperty()
        property.SetRepresentationToWireframe()
        renderer.AddActor(actor)
        OrigLayers.append(actor)

    return OrigLayers


OrigLayers = originalLayer()


for icount, file in enumerate(ListFiles):
    reader = vtkUnstructuredGridReader()
    reader.SetFileName(file)
    reader.Update()

    output = reader.GetOutput()
    output_port = reader.GetOutputPort()

    getScalars = vtkExtractVectorComponents()
    getScalars.SetInputData(output)
    getScalars.Update()

    getScalars.Update()
    output = getScalars.GetOutput()
    output_port = getScalars.GetOutputPort()

    mapper = vtkDataSetMapper()
    mapper.SetInputConnection(output_port)
    mapper.SetScalarRange(scalar_range)
    mapper.SetScalarVisibility(1)
    # mapper.SetLookupTable(lut)

    actor1 = vtkActor()
    actor1.SetMapper(mapper)
    renderer.AddActor(actor1)
    ListofActors.append(actor1)
    ListofReaders.append(reader)
    ListofMappers.append(mapper)

    ## add cube axes
    # cube_axes = vtkCubeAxesActor()
    # renderer.AddActor(cube_axes)
    #
    # cube_axes.SetBounds(actor1.GetBounds())
    # cube_axes.SetCamera(renderer.GetActiveCamera())
    # cube_axes.SetXLabelFormat("%6.1f")
    # cube_axes.SetYLabelFormat("%6.1f")
    # cube_axes.SetZLabelFormat("%6.1f")
    # cube_axes.SetFlyModeToOuterEdges()

## scalar bar, function has not been developed yet
# scalarbar = vtkScalarBarActor()
# renderer.AddActor(scalarbar)
# scalarbar.SetLookupTable(lut)
#
# scalarbar.SetTitle("Scalar Bar")
# scalarbar.GetLabelTextProperty().SetColor(0, 0, 0)
# scalarbar.GetTitleTextProperty().SetColor(0, 0, 0)
# scalarbar.SetLabelFormat('%.2f')
# scalarbar.SetPosition(0.9, 0.3)
#
# scalarbar_widget = vtkScalarBarWidget()
# scalarbar_widget.SetInteractor(renderWindowInteractor)
# scalarbar_widget.SetScalarBarActor(scalarbar)
# scalarbar_widget.On()

renderer.SetBackground(1, 1, 1)
renderer.ResetCamera()


class Representation:
    Points = 0
    Wireframe = 1
    Surface = 2
    SurfaceWithEdges = 3


class ModeShapes:
    M_1,M_2,M_3,M_4,M_5,M_6,M_7,M_8,M_9,M_10 = 0,1,2,3,4,5,6,7,8,9

# Representation Callbacks
def update_representation(ListofActors, mode):
    for actor in ListofActors:
        property = actor.GetProperty()
        if mode == Representation.Points:
            property.SetRepresentationToPoints()
            property.SetPointSize(5)
            property.EdgeVisibilityOff()
        elif mode == Representation.Wireframe:
            property.SetRepresentationToWireframe()
            property.SetPointSize(1)
            property.EdgeVisibilityOff()
        elif mode == Representation.Surface:
            property.SetRepresentationToSurface()
            property.SetPointSize(1)
            property.EdgeVisibilityOff()
        elif mode == Representation.SurfaceWithEdges:
            property.SetRepresentationToSurface()
            property.SetPointSize(1)
            property.EdgeVisibilityOn()


def update_mode_shapes(ListofReader, modeshape):
    adr = dirName + "\\" + str(modeshape + 1) + "/*.vtk"
    scalar_range = GetModeScalar(modeshape)
    TempFiles = glob.glob(adr)
    for icount, temFile in enumerate(TempFiles):
        ListofReader[icount].SetFileName(temFile)
        ListofReader[icount].Update()
        ListofMappers[icount].SetScalarRange(scalar_range)
    ctrl.view_update()


@state.change("mesh_representation")
def update_mesh_representation(mesh_representation, **kwargs):
    update_representation(ListofActors, mesh_representation)
    ctrl.view_update()


@state.change("modeShapes")
def update_mode_shapeaaa(modeShapes, **kwargs):
    update_mode_shapes(ListofReaders, modeShapes)
    ctrl.view_update()

@state.change("graph_theme")
def update_theme(**kwargs):
    renderer.SetBackground(0.2, 0.2, 0.2)
    ctrl.view_update()

@state.change("resolution")
def update_resolution(resolution, **kwargs):
    renderer.SetBackground(resolution, resolution, resolution)
    ctrl.view_update()

@state.change("cube_axes_visibility")
def update_cube_axes_visibility(cube_axes_visibility, **kwargs):
    for Layer in OrigLayers:
        Layer.SetVisibility(cube_axes_visibility)
    ctrl.view_update()


def mesh_representation():
    vuetify.VSelect(
        # Representation
        v_model=("mesh_representation", Representation.Surface),
        items=(
            "representations",
            [
                {"text": "Points", "value": 0},
                {"text": "Wireframe", "value": 1},
                {"text": "Surface", "value": 2},
                {"text": "SurfaceWithEdges", "value": 3},
            ],
        ),
        label="Representation",
        hide_details=True,
        dense=True,
        outlined=True,
        classes="pt-1",
    )

def choosingModeShapes():
    vuetify.VSelect(
        v_model=("modeShapes", ModeShapes.M_1),
        items=(
            "mode_shape",
            [
                {"text": "Mode 1", "value": 0},
                {"text": "Mode 2", "value": 1},
                {"text": "Mode 3", "value": 2},
                {"text": "Mode 4", "value": 3},
                {"text": "Mode 5", "value": 4},
                {"text": "Mode 6", "value": 5},
                {"text": "Mode 7", "value": 6},
                {"text": "Mode 8", "value": 7},
                {"text": "Mode 9", "value": 8},
                {"text": "Mode 10", "value": 9},
            ],
        ),
        label="Mode Shape",
        hide_details=True,
        dense=True,
        outlined=True,
        classes="pt-1",
    )


def standard_buttons():
    vuetify.VCheckbox(
        v_model=("cube_axes_visibility", True),
        change="graph_theme = $event",
        on_icon="mdi-cube-outline",
        off_icon="mdi-cube-off-outline",
        classes="mx-1",
        hide_details=True,
        dense=True,
    )
    vuetify.VCheckbox(
        v_model="$vuetify.theme.dark",
        on_icon="mdi-lightbulb-off-outline",
        off_icon="mdi-lightbulb-outline",
        classes="mx-1",
        hide_details=True,
        dense=True,
    )
    vuetify.VCheckbox(
        v_model=("viewMode", "local"), # VtkRemoteLocalView => {namespace}Mode=['local', 'remote']
        on_icon="mdi-lan-disconnect",
        off_icon="mdi-lan-connect",
        true_value="local",
        false_value="remote",
        classes="mx-1",
        hide_details=True,
        dense=True,
    )
    with vuetify.VBtn(icon=True, click=ctrl.view_reset_camera):
        vuetify.VIcon("mdi-crop-free")


local_assets = LocalFileManager(__file__)
local_assets.url("BIMSE", "./BIMSE.png")
local_assets.url("Cardiff_Uni", "./CardiffU.png")
# [...]


DEFAULT_RESOLUTION = 0.2

with SinglePageWithDrawerLayout(server, width= 500) as layout:

    layout.title.set_text("Structural Analysis BIMSE")

    with layout.toolbar:
        # toolbar components
        vuetify.VSpacer()
        vuetify.VDivider(vertical=True, dark = True, classes="mx-2")

        with vuetify.VBtn(href="https://bimse.uk/",
              icon=True,
              outlined=False,
              classes="pt-1",
              max_height=60,
              max_width=60,
              height="80px",
              hide_details=True,
                          ):
            vuetify.VImg(
                src=local_assets.BIMSE,
                max_height= 60,
                max_width = 60,
                aspectratio="1",
                height="80px",
                dense=False
            )

        vuetify.VSlider(
            v_model=("resolution", DEFAULT_RESOLUTION), # (var_name, initial_value)
            min=0, max=1, step=0.01,                      # min/max/step
            hide_details=True, dense=True,              # presentation params
            style="max-width: 200px",                   # css style
        )

        standard_buttons()

        with vuetify.VBtn(href="https://www.cardiff.ac.uk", icon=True, outlined=False, classes="pt-1", ):
            vuetify.VImg(
                src=local_assets.Cardiff_Uni,
                max_height= 60,
                max_width = 60,
                aspectratio="1",
                height="80px",
                dense=False
            )

    with layout.drawer as drawer:
        # drawer components
        drawer.width = 325
        vuetify.VDivider(classes="mb-2")

        with vuetify.VListItem(href = "https://bimse.uk/" , icon = True):
            with vuetify.VListItemIcon():
                vuetify.VIcon("mdi-home")
            with vuetify.VListItemContent():
                vuetify.VListItemTitle("Home")

        with ui_card(title="Choose Mode shapes"):
            choosingModeShapes()

        with ui_card(title="Choose Representation"):
            mesh_representation()
        pass

    with layout.content:
        with vuetify.VContainer(
            fluid=True,
            classes="pa-0 fill-height",
        ):
            view = vtk.VtkLocalView(renderer_window)
            ctrl.view_update = view.update              # capture view update method
            ctrl.view_reset_camera = view.reset_camera  # capture view reset_camera method
            ctrl.on_server_ready.add(view.update)       # update view once server is ready

    # with layout.drawer:
    #     with vuetify.VList(shaped=True, v_model=("selectedRoute", 0)):
    #         vuetify.VSubheader("Routes")
    #
    #
    #         with vuetify.VListItem(to="/foo"):
    #             with vuetify.VListItemIcon():
    #                 vuetify.VIcon("mdi-food")
    #             with vuetify.VListItemContent():
    #                 vuetify.VListItemTitle("Foo")
    #
    #         with vuetify.VListGroup(value=("true",), sub_group=True):
    #             with vuetify.Template(v_slot_activator=True):
    #                 vuetify.VListItemTitle("Bars")
    #             with vuetify.VListItemContent():
    #                 with vuetify.VListItem(v_for="id in [1]", to=("'/bar/' + id",)):
    #                     with vuetify.VListItemIcon():
    #                         vuetify.VIcon("mdi-peanut-outline")
    #                     with vuetify.VListItemContent():
    #                         vuetify.VListItemTitle("Bar")
    #                         vuetify.VListItemSubtitle("ID '{{id}}'")

if __name__ == "__main__":
    server.start()
