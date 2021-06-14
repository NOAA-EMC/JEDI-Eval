import os
def gen_bundle(projects, outdir, ufs=False):
    # args:
    # dict projects
    # str outdir - path to output CMakeLists.txt
    # ufs - boolean, default False, if True, sets FV3_FORECAST_MODEL to UFS
    # for a dictionary projects
    # projects['reponame'] = {'url': 'http://github.com/me/repo.git',
    #                         'branch'/'tag': 'develop',
    #                         'update': True,,
    #                        }
    outfile = os.path.join(outdir, 'CMakeLists.txt')
    with open(outfile, 'w') as outf:
        # write all these fixed lines first
        outf.write('cmake_minimum_required( VERSION 3.12 FATAL_ERROR )\n')
        outf.write('find_package( ecbuild 3.5 REQUIRED HINTS ${CMAKE_CURRENT_SOURCE_DIR} ${CMAKE_CURRENT_SOURCE_DIR}/../ecbuild)\n')
        outf.write('project( fv3-bundle VERSION 1.1.0 LANGUAGES C CXX Fortran )\n')
        outf.write('list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")\n')
        outf.write('include( ecbuild_bundle )\n')
        outf.write('set( ECBUILD_DEFAULT_BUILD_TYPE Release )\n')
        outf.write('set( ENABLE_MPI ON CACHE BOOL "Compile with MPI")\n')
        # intialize the bundle
        outf.write('ecbuild_bundle_initialize()\n')
        # these JEDI-CMake functions which I suspect are dependencies
        outf.write('ecbuild_bundle( PROJECT jedicmake GIT "https://github.com/jcsda-internal/jedi-cmake.git" BRANCH develop UPDATE )\n')
        outf.write('include( jedicmake/cmake/Functions/git_functions.cmake  )\n')
        # determine if UFS or FV3CORE
        fv3model = 'UFS' if ufs else 'FV3CORE'
        outf.write(f'set(FV3_FORECAST_MODEL "{fv3model}" CACHE STRING "Choose which MODEL to build with")\n')
        outf.write('set_property(CACHE FV3_FORECAST_MODEL PROPERTY STRINGS "FV3CORE" "UFS" "GEOS")\n')
        # loop through projects/repositories now
        for repo, repodict in projects.items():
            url = repodict['url']
            if 'branch' in repodict:
                branch = f'BRANCH {repodict["branch"]}'
            elif 'tag' in repodict:
                branch = f'TAG {repodict["tag"]}'
            else:
                raise KeyError(f'Neither branch nor tag defined for {repo}')
            update = 'UPDATE' if repodict['update'] else ''
            outf.write(f'ecbuild_bundle( PROJECT {repo} GIT "{url}" {branch} {update})\n')
        # finalize bundle
        outf.write('ecbuild_bundle_finalize()\n')
    print(f'Wrote bundle CMakeLists file to {outfile}')
