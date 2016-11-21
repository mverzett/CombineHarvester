#!/usr/bin/env python

import CombineHarvester.CombineTools.ch as ch
import os

cb = ch.CombineHarvester()

auxiliaries = os.environ['CMSSW_BASE'] + '/src/CombineHarvester/Httbar/data/'
aux_shapes = auxiliaries

addBBB = False

masses = ['400', '500', '600', '750']

# for mode in ['scalar']:#, 'pseudoscalar']:


width = '5'

for mode in ['A']:

    patterns = ['gg{mode}_pos-sgn-{width}pc-M', 'gg{mode}_pos-int-{width}pc-M',  'gg{mode}_neg-int-{width}pc-M']

    procs = {
        'sig': [pattern.format(mode=mode, width=width) for pattern in patterns],
        'bkg': ['WJets', 'tWChannel', 'tChannel', 'VV', 'ZJets', 'TT','TTV'],
        # 'bkg_mu':['QCDmujets'], # JAN: Ignore QCD for now because of extreme bbb uncertainties
        'bkg_mu':[],
        'bkg_e':[]
    }

    cats = [(0, 'mujets'), (1, 'ejets')]
    cat_to_id = {a:b for b, a in cats}

    cb.AddObservations(['*'], ['httbar'], ["8TeV"], [''], cats)
    cb.AddProcesses(['*'], ['httbar'], ["8TeV"], [''], procs['bkg'], cats, False)
    cb.AddProcesses(masses, ['httbar'], ["8TeV"], [''], procs['sig'], cats, True)

    print '>> Adding systematic uncertainties...'

    ### RATE UNCERTAINTIES

    # THEORY
    cb.cp().process(['VV']).AddSyst(
        cb, 'CMS_httbar_vvNorm_13TeV', 'lnN', ch.SystMap()(1.1))

    cb.cp().process(['TT']).AddSyst(
        cb, 'QCDscale_ttbar', 'lnN', ch.SystMap()(1.059))

    cb.cp().process(['tWChannel']).AddSyst(
        cb, 'CMS_httbar_tWChannelNorm_13TeV', 'lnN', ch.SystMap()(1.15))

    cb.cp().process(['tChannel']).AddSyst(
        cb, 'CMS_httbar_tChannelNorm_13TeV', 'lnN', ch.SystMap()(1.20))

    cb.cp().process(['WJets']).AddSyst(
        cb, 'CMS_httbar_WNorm_13TeV', 'lnN', ch.SystMap()(1.5))

    cb.cp().process(['ZJets']).AddSyst(
        cb, 'CMS_httbar_ZNorm_13TeV', 'lnN', ch.SystMap()(1.5))

    cb.cp().process(['TTV']).AddSyst(
        cb, 'CMS_httbar_TTVNorm_13TeV', 'lnN', ch.SystMap()(1.3))

    # EXPERIMENT
    cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(
        cb, 'lumi', 'lnN', ch.SystMap()(1.058))

    cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(
        cb, 'CMS_eff_trigger_m', 'lnN', ch.SystMap('bin_id')([cat_to_id['mujets']], 1.02))

    cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(
        cb, 'CMS_eff_trigger_e', 'lnN', ch.SystMap('bin_id')([cat_to_id['ejets']], 1.02))


    # GENERIC SHAPE UNCERTAINTIES
    shape_uncertainties = ['CMS_pileup', 'CMS_eff_b_13TeV', 'CMS_fake_b_13TeV', 'CMS_scale_j_13TeV', 'CMS_res_j_13TeV', 'CMS_METunclustered_13TeV']

    for shape_uncertainty in shape_uncertainties:
        cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(cb, shape_uncertainty, 'shape', ch.SystMap()(1.))

    shape_uncertainties_mu = ['CMS_eff_m']
    for shape_uncertainty in shape_uncertainties_mu:
        cb.cp().process(procs['sig'] + procs['bkg']).AddSyst(cb, shape_uncertainty, 'shape', ch.SystMap('bin_id')([cat_to_id['mujets']], 1.))

    # SPECIFIC SHAPE UNCERTAINTIES
    
    shape_uncertainties_tt = ['QCDscaleMERenorm_TT', 'QCDscaleMEFactor_TT', 'QCDscaleMERenormFactor_TT',
                              'Hdamp_TT', 'QCDscalePS_TT', 'TMass', 'pdf']

    for shape_uncertainty in shape_uncertainties_tt:
        cb.cp().process(['TT']).AddSyst(
            cb, shape_uncertainty, 'shape', ch.SystMap()(1.))

    print '>> Extracting histograms from input root files...'
    in_file = aux_shapes + 'templates1D_161110.root'
    cb.cp().backgrounds().ExtractShapes(
        in_file, '$BIN/$PROCESS', '$BIN/$PROCESS_$SYSTEMATIC')
    cb.cp().signals().ExtractShapes(
        in_file, '$BIN/$PROCESS$MASS', '$BIN/$PROCESS$MASS_$SYSTEMATIC')
    # in_file, '$BIN/$PROCESS', '$BIN/$PROCESS__$SYSTEMATIC')

    # print '>> Generating bbb uncertainties...'
    # bbb = ch.BinByBinFactory()
    # bbb.SetAddThreshold(0.1).SetFixNorm(True)
    # bbb.AddBinByBin(cb.cp().process(['reducible']), cb)

    # for mass in masses:
    #   norm_initial = norms[mode][int(mass)]

    #   cb.cp().process(['S0_neg_{mode}_M{mass}'.format(mode=mode, mass=mass), 'S0_{mode}_M{mass}'.format(mode=mode, mass=mass)]).ForEachProc(lambda p: p.set_rate(p.rate()/norm_initial))

    if addBBB:
        bbb = ch.BinByBinFactory().SetAddThreshold(0.).SetFixNorm(False)
        bbb.MergeBinErrors(cb.cp().backgrounds())
        bbb.AddBinByBin(cb.cp().backgrounds(), cb)

    print '>> Setting standardised bin names...'
    ch.SetStandardBinNames(cb)
    cb.PrintAll()

    writer = ch.CardWriter('$TAG/$MASS/$ANALYSIS_$CHANNEL_$BINID.txt',
                           # writer = ch.CardWriter('$TAG/$ANALYSIS_$CHANNEL_$BINID_$ERA.txt',
                           '$TAG/$ANALYSIS_$CHANNEL.input.root')
    # writer.SetVerbosity(100)
    writer.WriteCards('output/{mode}'.format(mode=mode), cb)
    print 'Try writing cards...'
    # import ROOT
    # f_out = ROOT.TFile('andrey_out.root', 'RECREATE')
    # cb.WriteDatacard("andrey_out.txt", 'andrey_out.root')
    # writer.WriteCards('output/andrey_cards/', cb)

print '>> Done!'

# Post instructions:
'''
combineTool.py -M T2W -i {scalar,pseudoscalar}/* -o workspace.root -P CombineHarvester.CombineTools.InterferenceModel:interferenceModel
combineTool.py -M Asymptotic -d */*/workspace.root --there -n .limit --parallel 4
combineTool.py -M CollectLimits */*/*.limit.* --use-dirs -o limits.json
plotLimits.py --y-title="Coupling modifier" --x-title="M_{A} (GeV)" limits_default.json 

combineTool.py -M Impacts -d workspace.root -m 600 --doInitialFit --robustFit 1
combineTool.py -M Impacts -d workspace.root -m 600 --robustFit 1 --doFits
# combineTool.py -M ImpactsFromScans -d workspace.root -m 600 --robustFit 1 --doFits  --robustFit on
combineTool.py -M Impacts -d workspace.root -m 600  -o impacts.json
plotImpacts.py -i impacts.json -o impacts
'''
