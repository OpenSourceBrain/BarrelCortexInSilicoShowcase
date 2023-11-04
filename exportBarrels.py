'''

This file will convert JSON files downloaded from the Janelia MouseLight project
(https://www.janelia.org/project-team/mouselight) in JSON format to NeuroML2

'''

import neuroml
import sys
import json
import neuroml.writers as writers
import random

def export_barrels(filename, ref):

    myrandom = random.Random(123456)

    print("Opened %s"%(filename))

    net_doc = neuroml.NeuroMLDocument(id='Net_%s'%ref)

    net = neuroml.Network(id=net_doc.id)
    net_doc.networks.append(net)

    planes = ['yz', 'xz', 'xy']

    data = {}
    line_count = 0

    for line in open(filename):
        entries = line.split(',')

        if entries[0]!='id':
            id = entries[0]
            name = entries[1]
            barrel_center_x = float(entries[2])
            barrel_center_y = float(entries[3])
            barrel_center_z = float(entries[4])
            normal_x = float(entries[5])
            normal_y = float(entries[6])
            normal_z = float(entries[7])
            radius = float(entries[8])
            
            
            cell_id = "barrel_"+name
            print("============================\nLooking at neuron id: %s"%(cell_id))
            cell_doc = neuroml.NeuroMLDocument(id=cell_id)
            cell = neuroml.Cell(id=cell_id)

            notes = '''\n    Cell %s downloaded from ...\n    and converted to NeuroML'''%cell_id

            cell.notes = notes


            net_doc.includes.append(neuroml.IncludeType(cell.id+'.cell.nml'))

            pop = neuroml.Population(id=name,
                        component=cell.id,
                        type="populationList")


            pop.properties.append(neuroml.Property('color','%s %s %s'%(0.7+0.05*myrandom.random(),0.7+0.05*myrandom.random(),0.7+0.05*myrandom.random())))

            inst = neuroml.Instance(id="0")
            pop.instances.append(inst)
            inst.location = neuroml.Location(x=barrel_center_x, y=barrel_center_y, z=barrel_center_z)
            net.populations.append(pop)

            cell_doc.cells.append(cell)
            cell.morphology = neuroml.Morphology(id='morph_%s'%cell_id)

            id_vs_seg = {}
            soma_id = 0
            soma = neuroml.Segment(id=soma_id, name='soma')
            cell.morphology.segments.append(soma)

            soma.proximal = neuroml.Point3DWithDiam(x=0 ,y=0,z=0,diameter=radius*2)

            ########################### CONFIRM!!!!  
            height = 500
            ########################### CONFIRM!!!!  

            soma.distal = neuroml.Point3DWithDiam(x=height*normal_x ,y=height*normal_y,z=height*normal_z,diameter=radius*2)
            id_vs_seg[0]=soma
            '''
            last_seg_id = -2

            offsets = {'axon':1000,'dendrite':1000000}

            for sg in offsets.keys():

                for a in n[sg]:
                    id = int(a['sampleNumber'])+offsets[sg]
                    name = '%s_%i'%(sg,id)
                    seg = neuroml.Segment(id=id, name=name)
                    seg.distal = neuroml.Point3DWithDiam(x=float(a['x']) ,y=float(a['y']),z=float(a['z']),diameter=float(a['radius'])*2)

                    parent = int(a['parentNumber'])

                    if parent==-1:
                        seg.parent = neuroml.SegmentParent(segments=soma.id)
                        parent = 0
                    else:
                        parent += offsets[sg]
                        seg.parent = neuroml.SegmentParent(segments=parent)

                    if parent!=last_seg_id or parent == 0 :
                        seg_parent = id_vs_seg[parent]
                        seg.proximal = neuroml.Point3DWithDiam(x=seg_parent.distal.x,
                                                            y=seg_parent.distal.y,
                                                            z=seg_parent.distal.z,
                                                            diameter=seg_parent.distal.diameter)
                        if parent == 0:
                            seg.proximal.diameter = seg.distal.diameter

                    last_seg_id = seg.id
                    id_vs_seg[id] = seg
                    cell.morphology.segments.append(seg)


            axon_seg_group = neuroml.SegmentGroup(id="axon_group",neuro_lex_id="GO:0030424")  # See http://amigo.geneontology.org/amigo/term/GO:0030424
            dend_seg_group = neuroml.SegmentGroup(id="dendrite_group",neuro_lex_id="GO:0030425")'''

            soma_seg_group = neuroml.SegmentGroup(id="soma_group",neuro_lex_id="GO:0043025")
            for seg in cell.morphology.segments:

                if 'axon' in seg.name:
                    axon_seg_group.members.append(neuroml.Member(segments=seg.id))
                elif 'soma' in seg.name:
                    soma_seg_group.members.append(neuroml.Member(segments=seg.id))
                elif 'dend' in seg.name:
                    dend_seg_group.members.append(neuroml.Member(segments=seg.id))
                else:
                    raise Exception("Segment: %s is not axon, dend or soma!"%seg)


            cell.morphology.segment_groups.append(soma_seg_group)
            #cell.morphology.segment_groups.append(dend_seg_group)
            #cell.morphology.segment_groups.append(axon_seg_group)


            nml_file = '%s.cell.nml'%cell.id

            writers.NeuroMLWriter.write(cell_doc,nml_file)

            print("Saved cell file to: "+nml_file)



            from pyneuroml.plot.PlotMorphology import plot_2D

            for plane in planes:

                p2d_file = '%s.cell.%s.png'%(cell.id,plane)

                gen_png=False
                if gen_png:
                    plot_2D(nml_file,
                            plane2d  = plane,
                            min_width = 0,
                            verbose= False,
                            nogui = True,
                            save_to_file=p2d_file,
                            square=True)


    nml_file = '%s.net.nml'%net.id

    writers.NeuroMLWriter.write(net_doc,nml_file)

    print("Saved network file to: "+nml_file)


if __name__ == "__main__":

    export_barrels('columns.csv', 'Barrels')
