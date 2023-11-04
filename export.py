'''

This file will convert ...

'''

import neuroml
import sys
import json
import neuroml.writers as writers
import random

def export_cell(filename, ref):


    print("Opened %s"%(filename))

    net_doc = neuroml.NeuroMLDocument(id='Net_%s'%ref)

    net = neuroml.Network(id=net_doc.id)
    net_doc.networks.append(net)

    planes = ['yz', 'xz', 'xy']

    data = {}
    line_count = 1

    vertices = []
    edges = []
    numEdgePoints = []
    edgePointCoordinates = {}
    epc_count = 0
    radius_count = 0

    mode = None
    for line in open(filename):

        line = line.strip()
        if '@1'==line:
            mode='VertexCoordinates'
            print('Converting to mode %s at line %i'%(mode, line_count))
        if '@2'==line:
            mode='GraphLabelsVERTEX'
            print('Converting to mode %s at line %i'%(mode, line_count))
        if '@3'==line:
            mode='EdgeConnectivity'
        if '@4'==line:
            mode='NumEdgePoints'
            print('Converting to mode %s at line %i'%(mode, line_count))
        if '@5'==line:
            mode='GraphLabelsEDGE'
        if '@6'==line:
            mode='EdgePointCoordinates'
            print('Converting to mode %s at line %i'%(mode, line_count))
            for ne in range(len(numEdgePoints)):
                edgePointCoordinates[ne] = []

        if '@7'==line:
            mode='Radius'
            print('Converting to mode %s at line %i'%(mode, line_count))

        if mode=='VertexCoordinates' and not '@' in line:
            if len(line)>0:
                print ('<%s>'%line)
                w = line.split(" ")
                vertices.append([float(w[0]),float(w[1]),float(w[2])])

        elif mode=='GraphLabelsVERTEX' and not '@' in line:
            pass
        elif mode=='EdgeConnectivity' and not '@' in line:
            if len(line)>0:
                print ('<%s>'%line)
                w = line.split(" ")
                edges.append([int(w[0]),int(w[1])])

        elif mode=='NumEdgePoints' and not '@' in line:
            if len(line)>0:
                print ('<%s>'%line)
                numEdgePoints.append(int(line))

        elif mode=='GraphLabelsEDGE' and not '@' in line:
            pass
        elif mode=='EdgePointCoordinates' and not '@' in line:
            if len(line)>0:
                edge = -1
                tot = 0
                print("EPC %s (tot: %s) for: %s"%(epc_count, tot, line))
                for ne in range(len(numEdgePoints)):
                    e = numEdgePoints[ne]
                    #print("   -- %i) Is epc %s between %s and %s?"%(ne, epc_count, tot, tot+e))
                    if epc_count>=tot and epc_count<tot+e:
                        edge = ne
                        break
                    tot+=e

                w = line.split(" ")
                edgePointCoordinates[edge].append([float(w[0]),float(w[1]),float(w[2])])

                epc_count+=1
                print("  Edge %s for: %s"%(edge, line))

        elif mode=='Radius' and not '@' in line:
            if len(line)>0:
                rad = float(line)
                epc_count+=1
                print("  Radius %s for: %s"%(edge, line))

        line_count+=1

    print('%i vertices: %s'%(len(vertices), vertices))
    print('%i edges: %s'%(len(edges), edges))
    print('%i numEdgePoints: %s'%(len(numEdgePoints), numEdgePoints))
    for epc in edgePointCoordinates:
        print("EPC %s: %i"%(epc, len(edgePointCoordinates[epc])))
    print()
    
    cell_id = "cell_"+ref
    print("============================\nLooking at neuron id: %s"%(cell_id))
    cell_doc = neuroml.NeuroMLDocument(id=cell_id)
    cell = neuroml.Cell(id=cell_id)

    notes = '''\n    Cell %s downloaded from ...\n    and converted to NeuroML'''%cell_id

    cell.notes = notes

    net_doc.includes.append(neuroml.IncludeType(cell.id+'.cell.nml'))

    pop = neuroml.Population(id=ref,
                component=cell.id,
                type="populationList")


    pop.properties.append(neuroml.Property('color','%s %s %s'%(myrandom.random(),myrandom.random(),myrandom.random())))

    inst = neuroml.Instance(id="0")
    pop.instances.append(inst)
    inst.location = neuroml.Location(x=0, y=0, z=0)
    net.populations.append(pop)

    cell_doc.cells.append(cell)
    cell.morphology = neuroml.Morphology(id='morph_%s'%cell_id)

    id_vs_seg = {}
    last_id_in_edge = {}
    
    offsets = {'axon':1000,'dendrite':1000000}
    last_seg_id = 0

    id_count = 0
    for i in range(len(edgePointCoordinates)):
        e = edges[i]
        epc = edgePointCoordinates[i]
        print('Edge %i: %s, %i points'%(i,e, len(epc)))

        for epi in range(len(epc)):
            if epi>0:
            
                id = id_count
                last_id_in_edge[i]=id

                sg = 'dendrite' if i > 0 else 'soma'
                name = '%s_%i'%(sg,id)
                seg = neuroml.Segment(id=id, name=name)


                p = epc[epi-1]
                d = epc[epi]
                if epi==1:
                    seg.proximal = neuroml.Point3DWithDiam(x=p[0] ,y=p[1],z=p[2],diameter=2)
                seg.distal = neuroml.Point3DWithDiam(x=d[0] ,y=d[1],z=d[2],diameter=2)

                if epi==1:
                    parent = last_id_in_edge[e[0]]
                else:
                    parent = id-1
                
                if parent==-1:
                    #seg.parent = neuroml.SegmentParent(segments=soma.id)
                    parent = 0
                else:
                    '''parent += offsets[sg]'''
                    seg.parent = neuroml.SegmentParent(segments=parent)

                print('  -- %s: %s, %s'%(seg, seg.distal, seg.parent))

            
                cell.morphology.segments.append(seg)

                id_count+=1

    print(last_id_in_edge)

    axon_seg_group = neuroml.SegmentGroup(id="axon_group",neuro_lex_id="GO:0030424")  # See http://amigo.geneontology.org/amigo/term/GO:0030424
    dend_seg_group = neuroml.SegmentGroup(id="dendrite_group",neuro_lex_id="GO:0030425")

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

        gen_png=True
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

    return cell_id


if __name__ == "__main__":


    myrandom = random.Random(123456)

    net_doc = neuroml.NeuroMLDocument(id='Net_All')

    net = neuroml.Network(id=net_doc.id)
    net_doc.networks.append(net)


    from pathlib import Path
    am_files = list(Path('.').glob("L45Peak_2*24*.am"))
    for f in am_files:
        fn = str(f)
        print('==================  %s'%fn)
        rr = fn.split('_')
        cell_id = export_cell(fn, "%s_%s"%(rr[0],rr[-2]))

        net_doc.includes.append(neuroml.IncludeType(cell_id+'.cell.nml'))

        pop = neuroml.Population(id='pop_%s'%cell_id,
                    component=cell_id,
                    type="populationList")


        pop.properties.append(neuroml.Property('color','%s %s %s'%(myrandom.random(),myrandom.random(),myrandom.random())))

        inst = neuroml.Instance(id="0")
        pop.instances.append(inst)
        inst.location = neuroml.Location(x=0, y=0, z=0)
        net.populations.append(pop)

        nml_file = '%s.net.nml'%net.id

        writers.NeuroMLWriter.write(net_doc,nml_file)

        print("Saved network file to: "+nml_file)
