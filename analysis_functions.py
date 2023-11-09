# ==================================================================================================
# --- Imports
# ==================================================================================================
# Import from standard library
import os
import shutil
from pathlib import Path

# Import third-party packages
import qrcode

# ==================================================================================================
# --- Functions for QR code and copying study to EOS
# ==================================================================================================


# To add QR codes to plot
def add_QR_code(fig, link):
    """
    Adds a QR code to a given matplotlib figure object.

    Parameters:
    fig (matplotlib.figure.Figure): The figure object to add the QR code to.
    link (str): The link to encode in the QR code.

    Returns:
    matplotlib.figure.Figure: The modified figure object with the QR code added.
    """

    qr = qrcode.QRCode(
        box_size=10,
        border=1,
    )
    qr.add_data(link)
    qr.make(fit=False)
    im = qr.make_image(fill_color="black", back_color="transparent")
    newax = fig.add_axes([0.9, 0.9, 0.05, 0.05], anchor="NE", zorder=1)
    newax.imshow(im, resample=False, interpolation="none", filternorm=False)
    # Add link below qrcode
    newax.annotate(
        "dum",
        xy=(0, 0),
        xytext=(0, 200),
        fontsize=15,
        url=link,
        bbox=dict(color="white", alpha=1e-6, url=link),
        alpha=0,
    )
    # Hide X and Y axes label marks
    newax.xaxis.set_tick_params(labelbottom=False)
    newax.yaxis.set_tick_params(labelleft=False)
    # Hide X and Y axes tick marks
    newax.set_xticks([])
    newax.set_yticks([])
    newax.set_axis_off()

    return fig


def copy_study_on_eos(
    study_name="example_HL_tunescan",
    path_study="/afs/cern.ch/work/u/user/private/example_DA_study/master_study/",
    path_EOS="/eos/home-u/user/save_simulations/",
    type_analysis="tune_scan",
    copy_master_jobs=True,
    copy_analysis=True,
    copy_tree_scripts=True,
    copy_scan=True,
):
    """
    Copy a study to EOS.

    Args:
        study_name (str): Name of the study from which the scans are produced.
        path_study (str): Path to the main study directory.
        path_EOS (str): Path to the EOS directory where the study will be copied.
        type_analysis (str): Type of analysis, corrsponding to the name of the folder in which the
            analysis is stored.
        copy_master_jobs (bool): Whether to copy the master jobs.
        copy_analysis (bool): Whether to copy the analysis, assumed as a jupyter notebook in the
            folder analysis/{type_analysis}/
        copy_tree_scripts (bool): Whether to copy the scripts to generate the scan.
        copy_scan (bool): Whether to copy the scan results.

    Returns:
        None
    """
    # Define path on EOS and create directory it if it does not exist
    path_archive = path_EOS + study_name + "/"
    Path(path_archive).mkdir(parents=True, exist_ok=True)

    # Copy all master jobs if requested
    if copy_master_jobs:
        shutil.copytree(
            path_study + "master_jobs", path_archive + "master_jobs", dirs_exist_ok=True
        )

    # Copy analysis if requested
    if copy_analysis:
        suffix_analysis = f"analysis/{type_analysis}/analysis_" + study_name + ".ipynb"
        path_source_analysis = path_study + suffix_analysis
        path_destination_analysis = path_archive + suffix_analysis
        os.makedirs(os.path.dirname(path_destination_analysis), exist_ok=True)
        shutil.copy(path_source_analysis, path_destination_analysis)

    # Copy scripts to generate the scan if requested
    if copy_tree_scripts:
        suffix_scripts = [
            "001_make_folders_" + study_name + ".py",
            "002_chronjob.py",
            "003_postprocessing.py",
        ]
        for suffix in suffix_scripts:
            path_source = path_study + suffix
            path_destination = path_archive + suffix
            shutil.copy(path_source, path_destination)

    # Copy scan is requested
    if copy_scan:
        print("Start copying scan, this may take a while...")
        shutil.copytree(
            path_study + "scans/" + study_name,
            path_archive + "/scans/" + study_name,
            dirs_exist_ok=True,
        )


def archive_and_clean(study_name, path_EOS):
    """
    Archives the study folder on EOS and exports as a zip file, then deletes the original folder.

    Args:
        study_name (str): Name of the study folder to archive.
        path_EOS (str): Path to the EOS directory where the archive will be exported.

    Returns:
        None
    """
    path_archive = path_archive = path_EOS + study_name + "/"

    # Convert the archive to a zip file, and export to EOS
    shutil.make_archive(path_archive, "zip", path_EOS, path_archive.split("/")[-1])

    # Delete the folder archive
    shutil.rmtree(path_archive)
