import os
from argparse import ArgumentParser, RawTextHelpFormatter
from bids.grabbids import BIDSLayout
from pyaffineprep.subject_data import SubjectData
from pyaffineprep.workhorse import do_subject_preproc


def get_parser():
    parser = ArgumentParser(description='pyaffineprep',
                            formatter_class=RawTextHelpFormatter)
    parser.add_argument(
        'bids_dir', action='store', help='the root folder of a BIDS valid '
        'dataset (sub-XXXXX folders should be found at the top level in '
        'this folder).')
    parser.add_argument('output_dir', action='store',
                        help='the output path for the outcomes of '
                        'preprocessing and visual reports')
    parser.add_argument('analysis_level', choices=['participant'],
                        help='processing stage to be run, only '
                        '"participant" in the case of '
                        'pyaffineprep (see BIDS-Apps specification).')

    g_bids = parser.add_argument_group('Options for filtering BIDS queries')
    g_bids.add_argument(
        '--participant_label', '--participant-label', action='store',
        nargs='+',
        help='one or more participant identifiers (the sub- prefix can be '
        'removed)')
    g_bids.add_argument('-t', '--task-id', action='store',
                        help='select a specific task to be processed')
    g_bids.add_argument('-r', '--run-id', action='store',
                        help='select a specific run id to be processed')

    g_conf = parser.add_argument_group('Workflow configuration')
    g_conf.add_argument(
        '--ignore', required=False, action='store', nargs="+", default=[],
        choices=['slicetiming', 'mc', 'coreg'],
        help='ignore selected aspects of the input dataset to disable '
        'corresponding parts of the workflow')
    g_conf.add_argument('--resample', action='store_true',
                        help='apply transformations to output images at the'
                        ' end')

    return parser

if __name__ == "__main__":
    opts = get_parser().parse_args()
    bids_dir = os.path.abspath(opts.bids_dir)
    output_dir = os.path.abspath(opts.output_dir)
    subject_label = opts.participant_label
    if subject_label is None:
        raise RuntimeError(
            "You must specify subjects with the --participant-label option")
    layout = BIDSLayout(bids_dir)

    if "slicetiming" not in opts.ignore:
        raise RuntimeError("Disable slicetiming (broken code!) with "
                           " --ignore slicetiming")

    fine_opts = {}
    for opt in ["task", "run"]:
        val = getattr(opts, "%s_id" % opt)
        if val is not None:
            fine_opts[opt] = val
    for subject in opts.participant_label:
        subject_data = SubjectData()
        func_files = [stuff.filename for stuff in layout.get(
            subject=subject, type="bold", modality="func", **fine_opts)]
        if len(func_files) < 1:
            raise RuntimeError(
                "No data functional found for subject %s" % subject)
        subject_data.func = func_files
        anat_files = [stuff.filename for stuff in layout.get(
            subject=subject, modality="anat")]
        if len(anat_files) < 1:
            raise RuntimeError("No data anat found for subject % subject")
        subject_data.anat = anat_files[0]

        subject_data.output_dir = os.path.join(
            output_dir, "sub-%s" % subject)
        slicetiming = None
        # metadata = layout.get_metadata(subject_data.func[0])
        # if "SliceTiming" in metadata:
        #     slicetiming = metadata["SliceTiming"]

        # preproc data
        subject_data.sanitize()
        print subject_data
        do_subject_preproc(
            subject_data, concat=True, coregister="coreg" not in opts.ignore,
            tsdiffana=True, realign="mc" not in opts.ignore, report=True,
            reslice=opts.resample, write_output_images=1,
            # slicetiming=slicetiming,
        )
