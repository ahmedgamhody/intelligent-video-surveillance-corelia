import {
  Button,
  Modal,
  Select,
  Label,
  Spinner,
  ToggleSwitch,
  Tooltip,
} from "flowbite-react";
import { TextInput, FileInput } from "flowbite-react";
import { FieldType, TModalType } from "../../types";
import { useState } from "react";
import { useAppDispatch } from "../../store/hooks";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import axios from "axios";
import {
  addChannel,
  setSelectedChannel,
} from "../../store/channel/channelSlice";
import { CirclePlus, Settings, Trash2 } from "lucide-react";
import { TSources } from "../../interfaces";

const initialFieldType: FieldType = {
  name: "",
  confidence: 25,
  overlapping: 75,
  augment: false,
  realTimeMode: true,
  tracking: true,
  withReId: false,
};

const apiUrl = import.meta.env.VITE_APP_CREATE_CHANNEL;
const modalsOptions = [
  "Default",
  "Pose",
  "Car-types",
  "Car-damages",
  "Containers",
  "Facial-expressions",
  "Fights and Weapons",
  "Fire and Smoke",
  "Vests and Helmets",
  "Hats and Gloves",
];
const tasksOptions = ["detection", "segmentation", "estimation"];
const weightsOptions = ["nano", "small", "medium", "large", "x-large"];
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export default function AddChannelModal({ openModal, setOpenModal }: any) {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState(initialFieldType);
  const [sources, setSources] = useState<TSources[]>([]);
  const [models, setModels] = useState<TModalType[]>([]);
  const dispatch = useAppDispatch();
  const navigate = useNavigate();

  const handleAddModal = () => {
    const lastModal = models[models.length - 1];

    if (!lastModal) {
      setModels([{ name: "", task: "", weight: "" }]);
      return;
    }

    const isLastModalFilled =
      lastModal.name.trim() !== "" &&
      lastModal.task.trim() !== "" &&
      lastModal.weight.trim() !== "";

    if (!isLastModalFilled) {
      alert("Please complete the previous modal before adding a new one.");
      return;
    }

    setModels([...models, { name: "", task: "", weight: "" }]);
  };

  const handleChange = (
    index: number,
    field: keyof TModalType,
    value: string
  ) => {
    const updatedModals = [...models];
    updatedModals[index][field] = value;
    setModels(updatedModals);
  };

  const handleDeleteModal = (index: number) => {
    const updatedModals = models.filter((_, i) => i !== index);
    setModels(updatedModals);
  };

  const handleAddSource = () => {
    const lastSource = sources[sources.length - 1];

    if (!lastSource) {
      setSources([{ source_name: "", source: "", type: "url" }]);
      return;
    }

    const isLastSourceFilled =
      lastSource.source_name.trim() !== "" &&
      lastSource.type &&
      (lastSource.type === "url"
        ? typeof lastSource.source === "string" &&
          lastSource.source.trim() !== ""
        : lastSource.source instanceof File);

    if (!isLastSourceFilled) {
      alert("Please complete the previous source before adding a new one.");
      return;
    }

    setSources([...sources, { source_name: "", source: "", type: "url" }]);
  };

  const handleChangeSources = (
    index: number,
    field: keyof TSources,
    value: string | File
  ) => {
    const updatedSources = [...sources];

    // Type guard to ensure value matches the field type
    if (field === "source_name" && typeof value === "string") {
      updatedSources[index][field] = value;
    } else if (
      field === "source" &&
      (typeof value === "string" || value instanceof File)
    ) {
      updatedSources[index][field] = value;
    } else if (field === "type" && (value === "url" || value === "file")) {
      updatedSources[index][field] = value;
    } else {
      console.error("Invalid value type for field:", field);
      return;
    }

    setSources(updatedSources);
  };
  const handleDeleteSource = (index: number) => {
    const updatedSources = sources.filter((_, i) => i !== index);
    setSources(updatedSources);
  };

  const submitHandler = async () => {
    const FinalFormData = new FormData();
    FinalFormData.append("channel_name", formData.name || "");
    FinalFormData.append("realtime_mode", String(formData.realTimeMode));
    FinalFormData.append(
      "confidence_threshold",
      String(Number(formData.confidence))
    );
    FinalFormData.append(
      "overlapping_threshold",
      String(Number(formData.overlapping))
    );
    FinalFormData.append("tracking", String(formData.tracking));
    FinalFormData.append("reid", String(formData.withReId));
    FinalFormData.append("augmentation_mode", String(formData.augment));

    FinalFormData.append("models", JSON.stringify(models));

    FinalFormData.append(
      "sources_names",
      JSON.stringify(sources.map((s) => s.source_name))
    );

    FinalFormData.append(
      "urls_sources",
      JSON.stringify(
        sources.filter((s) => s.type === "url").map((s) => s.source)
      )
    );

    sources
      .filter((s) => s.type === "file")
      .forEach((s) => {
        if (s.file) {
          FinalFormData.append("files_sources", s.file);
        }
      });

    try {
      setLoading(true);
      const response = await axios.post(`${apiUrl}`, FinalFormData);
      console.log("Response:", response.data);
      if (response.data && formData.name) {
        dispatch(addChannel(formData.name));
        dispatch(setSelectedChannel(formData.name));
      }

      navigate("/");
      setLoading(false);
      setOpenModal(false);
      toast.success(`${response.data.detail}`);
      setFormData(initialFieldType);
      setSources([]);
      setModels([]);
    } catch (error) {
      console.error("Error:", error);
      toast.error("Something went wrong");
      setLoading(false);
    }
  };

  return (
    <div>
      {/* Add Channel Modal */}
      <Modal
        show={openModal}
        size={"2xl"}
        onClose={() => {
          setOpenModal(false);
          setFormData(initialFieldType);
          setSources([]);
          setModels([]);
        }}
      >
        <Modal.Header>Add Channel</Modal.Header>
        <Modal.Body>
          <div className="flex flex-col gap-4 ">
            {/* Name */}
            <div className="flex  gap-3 flex-col">
              <Label
                htmlFor="name"
                value="Channel Name"
                className="text-lg text-secondary font-bold"
              />
              <TextInput
                className="w-full"
                id="name"
                type="text"
                placeholder="Channel Name"
                required
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
              />
            </div>
            {/* Sources */}
            <div className="mt-3">
              <div className="flex items-center justify-between mt-3">
                <h1 className="text-lg text-secondary font-bold my-2">
                  Sources
                </h1>
                <Tooltip content="Add Source">
                  <CirclePlus
                    strokeWidth={3}
                    className="text-secondary cursor-pointer"
                    onClick={handleAddSource}
                  />
                </Tooltip>
              </div>
              <div className="flex flex-col gap-4 mt-3 ">
                {/* Sources Labels */}
                {sources.length > 0 && (
                  <div className="flex  items-center justify-between mb-3">
                    <Label htmlFor="source-name" value="Source Name" />
                    <Label htmlFor="type" value="Type" />
                    <Label htmlFor="source" value="Source" />
                    <Label htmlFor="delete-source" value="Delete" />
                  </div>
                )}

                {sources?.map((source, index) => (
                  <div key={index} className="flex gap-3 mb-3 items-center">
                    {/* Source Name */}
                    <TextInput
                      id={`source-name-${index}`}
                      placeholder="Enter Source Name"
                      value={source.source_name}
                      onChange={(e) =>
                        handleChangeSources(
                          index,
                          "source_name",
                          e.target.value
                        )
                      }
                    />

                    {/* Selector for URL or File */}
                    <Select
                      value={source.type}
                      onChange={(e) =>
                        handleChangeSources(index, "type", e.target.value)
                      }
                      aria-label="Select URL or File type"
                    >
                      <option value="url">URL</option>
                      <option value="file">File</option>
                    </Select>

                    {/* URL Input */}
                    {source.type === "url" && (
                      <div>
                        <TextInput
                          id={`url-${index}`}
                          type="url"
                          placeholder="Enter URL"
                          value={source.source as string}
                          onChange={(e) =>
                            handleChangeSources(index, "source", e.target.value)
                          }
                        />
                      </div>
                    )}

                    {/* File Input */}
                    {source.type === "file" && (
                      <div>
                        <FileInput
                          id={`file-${index}`}
                          onChange={(e) =>
                            e.target.files &&
                            handleChangeSources(
                              index,
                              "source",
                              e.target.files[0]
                            )
                          }
                        />
                      </div>
                    )}

                    {/* Delete Button */}
                    <Trash2
                      color="red"
                      className="flex mx-auto cursor-pointer"
                      onClick={() => handleDeleteSource(index)}
                    />
                  </div>
                ))}
              </div>
            </div>
            {/* Models Section */}
            <div className="flex items-center justify-between mt-3">
              <h1 className="text-lg text-secondary font-bold my-2">Models</h1>
              <Tooltip content="Add Model">
                <CirclePlus
                  strokeWidth={3}
                  className="text-secondary cursor-pointer"
                  onClick={() => handleAddModal()}
                />
              </Tooltip>
            </div>
            {/* Models Labels */}
            {models.length > 0 && (
              <div className="flex  items-center justify-between mb-3">
                <Label className="w-1/3" htmlFor="modal" value="Model" />
                <Label className="w-1/3" htmlFor="task" value="Task" />
                <Label className="w-1/3" htmlFor="weight" value="Weight" />
              </div>
            )}
            {/* Models Inputs */}
            <div>
              {models?.map((modal, index) => (
                <div key={index} className="flex gap-3 mb-3 items-center">
                  <Select
                    onChange={(e) =>
                      handleChange(index, "name", e.target.value)
                    }
                    value={modal.name}
                    className="w-1/3"
                  >
                    <option className="hidden">Select Model</option>
                    {modalsOptions?.map((model) => (
                      <option key={model} value={model}>
                        {model}
                      </option>
                    ))}
                  </Select>

                  <Select
                    onChange={(e) =>
                      handleChange(index, "task", e.target.value)
                    }
                    value={modal.task}
                    className="w-1/3"
                  >
                    <option className="hidden">Select Task</option>
                    {tasksOptions?.map((task) => (
                      <option key={task} value={task}>
                        {task}
                      </option>
                    ))}
                  </Select>

                  <Select
                    onChange={(e) =>
                      handleChange(index, "weight", e.target.value)
                    }
                    value={modal.weight}
                    className="w-1/3"
                  >
                    <option className="hidden">Select Weight</option>
                    {weightsOptions?.map((weight) => (
                      <option key={weight} value={weight}>
                        {weight}
                      </option>
                    ))}
                  </Select>

                  <div className="flex gap-1 items-center">
                    <Settings className=" cursor-pointer" />
                    <Trash2
                      color="red"
                      className=" cursor-pointer"
                      onClick={() => handleDeleteModal(index)}
                    />
                  </div>
                </div>
              ))}
            </div>
            {/*  Configuration */}
            <div>
              <h1 className="text-lg text-secondary font-bold my-2">
                Configuration
              </h1>
              <div className="flex my-3 gap-6 flex-wrap mt-4">
                <div className="flex gap-3">
                  {/* Confidence Slider */}
                  <div className="flex gap-2 items-center">
                    <Label htmlFor="confidence" value={`Confidence`} />
                    <TextInput
                      id="confidence"
                      type="number"
                      value={formData.confidence}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          confidence: Number(e.target.value),
                        })
                      }
                      placeholder="confidence"
                    />
                  </div>

                  {/* Overlapping */}
                  <div className="flex gap-2 items-center">
                    <Label htmlFor="overlapping" value={`Overlapping`} />
                    <TextInput
                      id="overlapping"
                      type="number"
                      value={formData.overlapping}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          overlapping: Number(e.target.value),
                        })
                      }
                      placeholder="confidence"
                    />
                  </div>
                </div>

                <div className="flex justify-between w-full gap-4">
                  {/* Augmentation mode */}
                  <div className="flex items-center justify-between w-1/2">
                    <Label htmlFor="augment" value="Augmentation mode" />
                    <ToggleSwitch
                      id="augment"
                      checked={formData.augment}
                      theme={{
                        toggle: {
                          checked: {
                            color: {
                              cyan: "bg-secondary",
                            },
                          },
                        },
                      }}
                      color="cyan"
                      onChange={() =>
                        setFormData({
                          ...formData,
                          augment: !formData.augment,
                        })
                      }
                    />
                  </div>

                  {/* Real-time mode */}
                  <div className="flex items-center justify-between w-1/2">
                    <Label htmlFor="realTimeMode" value="Real-time mode" />
                    <ToggleSwitch
                      id="realTimeMode"
                      checked={formData.realTimeMode}
                      theme={{
                        toggle: {
                          checked: {
                            color: {
                              cyan: "bg-secondary",
                            },
                          },
                        },
                      }}
                      color="cyan"
                      onChange={() =>
                        setFormData({
                          ...formData,
                          realTimeMode: !formData.realTimeMode,
                        })
                      }
                    />
                  </div>
                </div>
                {/* Tracking */}
                <div className="flex justify-between w-full gap-4">
                  <div className="flex items-center justify-between w-1/2">
                    <Label htmlFor="tracking">Tracking</Label>
                    <ToggleSwitch
                      id="tracking"
                      checked={formData.tracking}
                      theme={{
                        toggle: {
                          checked: {
                            color: {
                              cyan: "bg-secondary",
                            },
                          },
                        },
                      }}
                      color="cyan"
                      onChange={() => {
                        const newTracking = !formData.tracking;

                        setFormData({
                          ...formData,
                          tracking: newTracking,
                          withReId: newTracking ? formData.withReId : false,
                        });
                      }}
                    />
                  </div>
                  {/* ReID */}
                  <div className="flex items-center justify-between w-1/2">
                    <Label>ReID</Label>
                    <ToggleSwitch
                      disabled={!formData.tracking}
                      checked={formData.withReId}
                      theme={{
                        toggle: {
                          checked: {
                            color: {
                              cyan: "bg-secondary",
                            },
                          },
                        },
                      }}
                      color="cyan"
                      onChange={() => {
                        setFormData({
                          ...formData,
                          withReId: !formData.withReId,
                        });
                      }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </Modal.Body>
        <Modal.Footer>
          <Button
            disabled={
              !formData.name ||
              loading ||
              !models[0]?.weight ||
              !sources[0]?.source
            }
            onClick={submitHandler}
          >
            {loading ? (
              <div className="flex items-center">
                <Spinner />
                <span className="pl-3">Verify...</span>{" "}
              </div>
            ) : (
              "Verify"
            )}
          </Button>
          <Button
            color="gray"
            onClick={() => {
              setFormData(initialFieldType);
              setOpenModal(false);
            }}
          >
            Cancel
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
}
