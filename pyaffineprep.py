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

    parser.add_argument('--do-stc', action='store_true',
                        help='do slice-timing correction')
    parser.add_argument('--no-mc', action='store_true',
                        help='disable motion-correction')
    parser.add_argument('--no-coreg', action='store_true',
                        help='disable coregistration (to anat)')
    parser.add_argument('--resample', action='store_true',
                        help='apply transformations to output images at the'
                        ' end')

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

    return parser

if __name__ == "__main__":
    opts = get_parser().parse_args()
    bids_dir = os.path.abspath(opts.bids_dir)
    output_dir = os.path.abspath(opts.output_dir)
    subject_list = opts.participant_label
    layout = BIDSLayout(bids_dir)

    if opts.do_stc:
        raise NotImplementedError("--do-stc option is broken!")

    for sidx in subject_list:
        print sidx, bids_dir
        subject_data = SubjectData()
        subject_data.func = [stuff.filename for stuff in layout.get(
            subject=sidx, type="bold", modality="func", task=opts.task_id,
            run=opts.run_id)]
        anat_files = [stuff.filename for stuff in layout.get(
            subject=sidx, modality="anat")]
        subject_data.anat = anat_files[0]
        subject_data.output_dir = os.path.join(output_dir, "sub-%s" % sidx)

        # preproc data
        subject_data.sanitize()
        print subject_data
        do_subject_preproc(
            subject_data, concat=True, coregister=not opts.no_coreg,
            stc=opts.do_stc, tsdiffana=True, realign=not opts.no_mc,
            report=True, reslice=opts.resample, write_output_images=1)
