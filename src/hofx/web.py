import os
import glob
import shutil
#import hofx

oz_all = ['omps_npp', 'omi_aura', 'ompstc8_npp']

def get_obs_lists(plot_dir):
    # search plot_dir and determine all unique instruments/ob types
    all_figs = glob.glob(os.path.join(plot_dir,'*.png'))
    # strip off most of the unneeded info
    all_figs = [os.path.basename(f) for f in all_figs]
    all_figs2 = [f.split('.')[0] for f in all_figs]
    all_obs = list(set(all_figs2))
    conv_list = []
    rad_list = []
    oz_list = []
    for ob in all_obs:
        if '_' not in ob:
            conv_list.append(ob)
        else:
            if ob not in oz_all:
                rad_list.append(ob)
            else:
                oz_list.append(ob)
    return conv_list, rad_list, oz_list


def gen_root_index(www_dir, template_dir, expname,
                   conv_list, rad_list, oz_list):
    # generate root index.html file
    templatefile = os.path.join(template_dir, 'index.html')
    with open(templatefile) as htmlin:
        # create HTML to replace in template
        rad_html = ''
        conv_html = ''
        oz_html = ''
        for rad in rad_list:
            rad_html = rad_html + \
                f'<a href="rad/{rad}/index.html">{rad.upper()}</a>\n'
        for conv in conv_list:
            conv_html = conv_html + \
                f'<a href="conv/{conv}/index.html">{conv.upper()}</a>\n'
        for oz in oz_list:
            oz_html = oz_html + \
                f'<a href="oz/{oz}/index.html">{oz.upper()}</a>\n'
        # find and replace in template
        replacements = {
            '{{EXPNAME}}': expname,
            '{{RADLIST}}': rad_html,
            '{{CONVLIST}}': conv_html,
            '{{OZLIST}}': oz_html,
            '{{CONTENTHTML}}': 'main.html',
            '{{HOMEPATH}}': '',
            '{{PANELH}}': '700px',
        }
        outfile = os.path.join(www_dir, 'index.html')
        with open(outfile, 'w') as htmlout:
            for line in htmlin:
                for src, target in replacements.items():
                    line = line.replace(src, target)
                htmlout.write(line)


def gen_sensor_index(htmlfile, templatefile, expname, mysensor,
                     radlist, convlist, ozlist):
    # creates index.html for the individual ob type pages
    with open(templatefile) as htmlin:
        # create HTML to replace in template
        rad_html = ''
        conv_html = ''
        oz_html = ''
        for rad in radlist:
            rad_html = rad_html + \
                f'<a href="../../rad/{rad}/index.html">{rad.upper()}</a>\n'
        for conv in convlist:
            conv_html = conv_html + \
                f'<a href="../../conv/{conv}/index.html">{conv.upper()}</a>\n'
        for oz in ozlist:
            oz_html = oz_html + \
                f'<a href="../../oz/{oz}/index.html">{oz.upper()}</a>\n'
        # find and replace in template
        replacements = {
            '{{EXPNAME}}': expname,
            '{{RADLIST}}': rad_html,
            '{{CONVLIST}}': conv_html,
            '{{OZLIST}}': oz_html,
            '{{CONTENTHTML}}': f'{mysensor}.html',
            '{{HOMEPATH}}': '../../index.html',
            '{{PANELH}}': '700px',
        }
        with open(htmlfile, 'w') as htmlout:
            for line in htmlin:
                for src, target in replacements.items():
                    line = line.replace(src, target)
                htmlout.write(line)


def gen_conv_page(htmlfile, templatefile, cycles, cycledirs, obtype):
    # generate main html page for each individual sensor
    with open(templatefile) as htmlin:
        # create javascript for all available cycles
        cychtml = ''
        for cyc in cycles:
            cychtml = cychtml + \
                f'validtimes.push({{displayName: "{cyc}", name: "{cyc}"}});\n'
        # create javascript for all variables
        varhtml = ''
        my_figs = glob.glob(os.path.join(
            cycledirs[0], f'{obtype}.*.hofxdiff.scatter.png'))
        vars = sorted([os.path.basename(c).split('.')[1]
                       for c in my_figs])
        for v in vars:
            varhtml = varhtml + \
                f'channels.push({{displayName: "{v}", name: "{v}"}});\n'
        # create javascript for all plot types
        plothtml = ''
        my_figs = glob.glob(os.path.join(
            cycledirs[0], f'{obtype}.{vars[0]}*.png'))
        plottypes = list(set(['.'.join(os.path.basename(c).split('.')[2:4]) for c in my_figs]))
        for p in plottypes:
            plothtml = plothtml + \
                f'plottypes.push({{displayName: "{p}", name: "{p}"}});\n'

        replacements = {
            '{{OBTYPE}}': obtype,
            '{{CYCLEPUSH}}': cychtml,
            '{{VARPUSH}}': varhtml,
            '{{PLOTPUSH}}': plothtml,
            '{{PLOT1}}': plottypes[0],
            '{{CYCLE1}}': cycles[0],
        }
        with open(htmlfile, 'w') as htmlout:
            for line in htmlin:
                for src, target in replacements.items():
                    line = line.replace(src, target)
                htmlout.write(line)


def gen_rad_page(htmlfile, templatefile, cycles, cycledirs, sensor):
    # generate main html page for each individual sensor
    with open(templatefile) as htmlin:
        # create javascript for all available cycles
        cychtml = ''
        for cyc in cycles:
            cychtml = cychtml + \
                f'validtimes.push({{displayName: "{cyc}", name: "{cyc}"}});\n'
        # create javascript for all channels
        chanhtml = ''
        my_figs = glob.glob(os.path.join(
            cycledirs[0], f'{sensor}.*hofxdiff.scatter.png'))
        chans = sorted([int(os.path.basename(c).split('.')[1].split('_')[3])
                        for c in my_figs])
        for ch in chans:
            chanhtml = chanhtml + \
                f'channels.push({{displayName: "{ch}", name: "{ch}"}});\n'
        # create javascript for all plot types
        plothtml = ''
        my_figs = glob.glob(os.path.join(
            cycledirs[0], f'{sensor}.brightness_temperature_channel_{chans[0]}*.png'))
        plottypes = list(set(['.'.join(os.path.basename(c).split('.')[2:4]) for c in my_figs]))
        for p in plottypes:
            plothtml = plothtml + \
                f'plottypes.push({{displayName: "{p}", name: "{p}"}});\n'

        replacements = {
            '{{SENSOR}}': sensor,
            '{{CYCLEPUSH}}': cychtml,
            '{{CHANNELPUSH}}': chanhtml,
            '{{PLOTPUSH}}': plothtml,
            '{{PLOT1}}': plottypes[0],
            '{{CYCLE1}}': cycles[0],
        }
        with open(htmlfile, 'w') as htmlout:
            for line in htmlin:
                for src, target in replacements.items():
                    line = line.replace(src, target)
                htmlout.write(line)


def gen_site(www_dir, plot_dirs, expname):
    # generate HTML for website depending on what figures, etc. are in plot_dirs
    # www_dir - string path to root of website
    # plot_dirs - list of string paths to each plot directory
    # expname - string name of experiment

    # determine location of HTML template files
    #template_dir = os.path.join(hofx.hofx_directory, 'cfg', 'templates', 'www')
    template_dir = os.path.join('/Users/corymartin/Documents/GitHub/hofxcs/src/hofx', 'cfg', 'templates', 'www')

    # get list of cycles
    cycles = [os.path.basename(c) for c in plot_dirs]

    # copy some static html files that do not need modified
    main_html = os.path.join(www_dir, 'main.html')
    shutil.copy(os.path.join(template_dir, 'main.html'), main_html)
    # copy the javascript
    main_js = os.path.join(www_dir, 'functions_main.js')
    shutil.copy(os.path.join(template_dir, 'functions_main.js'), main_js)

    # get all available obs types
    # for now just assume first cycle will have them all
    conv_list, rad_list, oz_list = get_obs_lists(plot_dirs[0])

    # create root index.html file
    gen_root_index(www_dir, template_dir, expname,
                   conv_list, rad_list, oz_list)

    # now for each observation type, make a directory and html
    for rad in rad_list:
        os.makedirs(os.path.join(www_dir, 'rad', rad))
        gen_sensor_index(os.path.join(www_dir, 'rad', rad, 'index.html'),
                         os.path.join(template_dir, 'index.html'),
                         expname, rad, rad_list, conv_list, oz_list)
        gen_rad_page(os.path.join(www_dir, 'rad', rad, f'{rad}.html'),
                     os.path.join(template_dir, 'radmain.html'),
                     cycles, plot_dirs, rad)
    for conv in conv_list:
        os.makedirs(os.path.join(www_dir, 'conv', conv))
        gen_sensor_index(os.path.join(www_dir, 'conv', conv, 'index.html'),
                         os.path.join(template_dir, 'index.html'),
                         expname, conv, rad_list, conv_list, oz_list)
        gen_conv_page(os.path.join(www_dir, 'conv', conv, f'{conv}.html'),
                     os.path.join(template_dir, 'convmain.html'),
                     cycles, plot_dirs, conv)
    for oz in oz_list:
        os.makedirs(os.path.join(www_dir, 'oz', oz))
        gen_sensor_index(os.path.join(www_dir, 'oz', oz, 'index.html'),
                         os.path.join(template_dir, 'index.html'),
                         expname, oz, rad_list, conv_list, oz_list)
        gen_conv_page(os.path.join(www_dir, 'oz', oz, f'{oz}.html'),
                     os.path.join(template_dir, 'ozmain.html'),
                     cycles, plot_dirs, oz)
